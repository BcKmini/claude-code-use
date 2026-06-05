use anyhow::{Context, Result};
use clap::Subcommand;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::PathBuf;

use crate::colors::*;

// Prices per 1M tokens (USD)
const PRICING: &[(&str, f64, f64)] = &[
    ("opus",   15.00, 75.00),
    ("sonnet",  3.00, 15.00),
    ("haiku",   0.25,  1.25),
];

const AGENT_MODELS: &[(&str, &str)] = &[
    ("orchestrator",        "opus"),
    ("planner",             "sonnet"),
    ("implementer",         "sonnet"),
    ("reviewer",            "sonnet"),
    ("tester",              "sonnet"),
    ("security-auditor",    "sonnet"),
    ("performance-optimizer","sonnet"),
    ("database-expert",     "sonnet"),
    ("documenter",          "haiku"),
];

// Estimated output:input ratio
const OUTPUT_RATIO: &[(&str, f64)] = &[
    ("opus",   3.5),
    ("sonnet", 2.5),
    ("haiku",  1.5),
];

fn budget_file() -> PathBuf {
    dirs::home_dir().unwrap().join(".claude").join("cost-budget.json")
}

fn snippets_file() -> PathBuf {
    dirs::home_dir().unwrap().join(".claude").join("snippets.json")
}

fn projects_dir() -> PathBuf {
    dirs::home_dir().unwrap().join(".claude").join("projects")
}

fn pricing(model: &str) -> (f64, f64) {
    PRICING.iter()
        .find(|(name, _, _)| model.contains(name))
        .map(|(_, i, o)| (*i, *o))
        .unwrap_or((3.00, 15.00)) // default sonnet
}

fn output_ratio(model: &str) -> f64 {
    OUTPUT_RATIO.iter()
        .find(|(name, _)| model.contains(name))
        .map(|(_, r)| *r)
        .unwrap_or(2.5)
}

fn estimate_tokens(text: &str) -> usize {
    text.len() / 4
}

fn calc_cost(input_tokens: usize, model: &str) -> f64 {
    let (inp_price, out_price) = pricing(model);
    let ratio = output_ratio(model);
    let output_tokens = (input_tokens as f64 * ratio) as usize;
    (input_tokens as f64 / 1_000_000.0 * inp_price)
        + (output_tokens as f64 / 1_000_000.0 * out_price)
}

#[derive(Debug, Serialize, Deserialize, Default)]
struct Budget {
    monthly: f64,
}

fn load_budget() -> Budget {
    budget_file()
        .exists()
        .then(|| std::fs::read_to_string(budget_file()).ok())
        .flatten()
        .and_then(|s| serde_json::from_str(&s).ok())
        .unwrap_or_default()
}

fn save_budget(b: &Budget) -> Result<()> {
    let path = budget_file();
    std::fs::write(path, serde_json::to_string_pretty(b)?)?;
    Ok(())
}

fn load_snippet_prompt(name: &str) -> Option<String> {
    let text = std::fs::read_to_string(snippets_file()).ok()?;
    let map: HashMap<String, serde_json::Value> = serde_json::from_str(&text).ok()?;
    map.get(name)?.get("prompt")?.as_str().map(|s| s.to_string())
}

// Parse JSONL files in ~/.claude/projects/ to get session usage
fn parse_sessions(days: i64) -> Vec<(String, String, u64, u64)> { // (date, model, input, output)
    let dir = projects_dir();
    if !dir.exists() { return Vec::new(); }
    let cutoff = chrono::Local::now() - chrono::Duration::days(days);
    let mut results = Vec::new();

    let Ok(project_dirs) = std::fs::read_dir(&dir) else { return Vec::new(); };
    for pd in project_dirs.filter_map(|e| e.ok()) {
        let Ok(files) = std::fs::read_dir(pd.path()) else { continue };
        for file in files.filter_map(|e| e.ok()) {
            let path = file.path();
            if path.extension().map(|e| e == "jsonl").unwrap_or(false) {
                let Ok(content) = std::fs::read_to_string(&path) else { continue };
                for line in content.lines() {
                    let Ok(val) = serde_json::from_str::<serde_json::Value>(line) else { continue };
                    // Look for usage events
                    if let Some(usage) = val.get("usage") {
                        let ts = val.get("timestamp")
                            .and_then(|t| t.as_str())
                            .unwrap_or("");
                        let Ok(dt) = chrono::DateTime::parse_from_rfc3339(ts) else { continue };
                        if dt < cutoff { continue; }
                        let date = dt.format("%Y-%m-%d").to_string();
                        let model = val.get("model")
                            .and_then(|m| m.as_str())
                            .unwrap_or("sonnet")
                            .to_string();
                        let inp = usage.get("input_tokens").and_then(|v| v.as_u64()).unwrap_or(0);
                        let out = usage.get("output_tokens").and_then(|v| v.as_u64()).unwrap_or(0);
                        results.push((date, model, inp, out));
                    }
                }
            }
        }
    }
    results
}

fn calc_session_cost(model: &str, input: u64, output: u64) -> f64 {
    let (inp_price, out_price) = pricing(model);
    (input as f64 / 1_000_000.0 * inp_price) + (output as f64 / 1_000_000.0 * out_price)
}

#[derive(Subcommand)]
pub enum CostCmd {
    /// Estimate cost for a prompt or snippet
    Estimate {
        /// Prompt text (or omit to use --snippet)
        prompt: Option<String>,
        /// Snippet name to estimate
        #[arg(long)] snippet: Option<String>,
        /// Number of agents (default: 1)
        #[arg(long, default_value = "1")] agents: usize,
        /// Variable substitutions KEY=VALUE
        #[arg(long, value_parser = parse_key_val)] var: Vec<(String, String)>,
    },
    /// Show recent session cost history
    History {
        #[arg(long, default_value = "7")] days: i64,
    },
    /// Show monthly cost summary
    Month {
        #[arg(long)] month: Option<String>,
    },
    /// Show per-agent cost breakdown
    Agents {
        #[arg(long, default_value = "7")] days: i64,
    },
    /// Set monthly budget
    SetBudget {
        amount: f64,
    },
    /// Print version
    Version,
}

fn parse_key_val(s: &str) -> Result<(String, String), String> {
    let parts: Vec<&str> = s.splitn(2, '=').collect();
    if parts.len() != 2 {
        return Err(format!("Expected KEY=VALUE, got '{s}'"));
    }
    Ok((parts[0].to_string(), parts[1].to_string()))
}

pub fn run(cmd: CostCmd) -> Result<()> {
    match cmd {
        CostCmd::Version => println!("claude-tools cost v1.0.0"),

        CostCmd::Estimate { prompt, snippet, agents, var } => {
            let text = if let Some(name) = snippet {
                load_snippet_prompt(&name)
                    .context(format!("Snippet '{}' not found.", name))?
            } else if let Some(p) = prompt {
                p
            } else {
                anyhow::bail!("Provide a prompt or --snippet NAME");
            };

            // Apply variable substitutions
            let mut filled = text.clone();
            for (k, v) in &var {
                filled = filled.replace(&format!("{{{{{k}}}}}"), v);
            }

            let tokens = estimate_tokens(&filled);
            let budget = load_budget();

            println!("{}", bold("Cost Estimate"));
            println!("{}", "-".repeat(50));
            println!("  Prompt tokens  : {}", cyan(&tokens.to_string()));
            println!();
            println!("{:<20} {:>10} {:>12}", bold("MODEL"), bold("TOKENS"), bold("COST"));
            println!("{}", "-".repeat(50));

            let models = if agents <= 1 {
                vec![("sonnet", tokens)]
            } else {
                AGENT_MODELS.iter()
                    .map(|(_, model)| (*model, tokens))
                    .collect()
            };

            let mut total = 0f64;
            let mut model_totals: HashMap<&str, (usize, f64)> = HashMap::new();
            for (model, t) in &models {
                let cost = calc_cost(*t, model);
                let entry = model_totals.entry(model).or_default();
                entry.0 += t;
                entry.1 += cost;
                total += cost;
            }

            let mut rows: Vec<_> = model_totals.iter().collect();
            rows.sort_by_key(|(k, _)| *k);
            for (model, (tok, cost)) in &rows {
                println!("{:<20} {:>10} {:>12}",
                    cyan(model),
                    tok,
                    yellow(&format!("${:.4}", cost)));
            }
            println!("{}", "-".repeat(50));
            println!("{:<20} {:>10} {:>12}",
                bold("TOTAL"),
                "",
                bold(&green(&format!("${:.4}", total))));

            if budget.monthly > 0.0 {
                let pct = total / budget.monthly * 100.0;
                println!("\nBudget: ${:.2}/month  ({:.1}% of monthly budget)",
                    budget.monthly, pct);
            }
        }

        CostCmd::History { days } => {
            let sessions = parse_sessions(days);
            if sessions.is_empty() {
                println!("No session data found in ~/.claude/projects/");
                return Ok(());
            }
            let mut by_date: HashMap<&str, f64> = HashMap::new();
            for (date, model, inp, out) in &sessions {
                *by_date.entry(date.as_str()).or_default() +=
                    calc_session_cost(model, *inp, *out);
            }
            let mut rows: Vec<_> = by_date.iter().collect();
            rows.sort_by_key(|(d, _)| *d);
            println!("{}", bold(&format!("{:<15} {:>10}", "DATE", "COST")));
            println!("{}", "-".repeat(30));
            for (date, cost) in &rows {
                println!("{:<15} {:>10}", date, yellow(&format!("${:.4}", cost)));
            }
            let total: f64 = rows.iter().map(|(_, c)| *c).sum();
            println!("{}", "-".repeat(30));
            println!("{:<15} {:>10}", bold("TOTAL"), green(&format!("${:.4}", total)));
        }

        CostCmd::Month { month } => {
            let sessions = parse_sessions(31);
            let target = month.unwrap_or_else(|| {
                chrono::Local::now().format("%Y-%m").to_string()
            });
            let total: f64 = sessions.iter()
                .filter(|(date, _, _, _)| date.starts_with(&target))
                .map(|(_, model, inp, out)| calc_session_cost(model, *inp, *out))
                .sum();
            let budget = load_budget();
            println!("{}", bold(&format!("Month: {}", target)));
            println!("  Total cost : {}", green(&format!("${:.4}", total)));
            if budget.monthly > 0.0 {
                let pct = total / budget.monthly * 100.0;
                let bar_len = (pct / 5.0).min(20.0) as usize;
                let bar = "#".repeat(bar_len) + &"-".repeat(20 - bar_len);
                println!("  Budget     : ${:.2}", budget.monthly);
                println!("  Usage      : [{bar}] {:.1}%", pct);
            }
        }

        CostCmd::Agents { days } => {
            let sessions = parse_sessions(days);
            println!("{}", bold(&format!("{:<24} {:<10} {:>10}", "AGENT", "MODEL", "EST. COST")));
            println!("{}", "-".repeat(50));

            let total_tokens: u64 = sessions.iter()
                .map(|(_, _, i, o)| i + o)
                .sum::<u64>()
                .max(10_000);

            for (agent, model) in AGENT_MODELS {
                let share = match *model {
                    "opus"   => 0.30,
                    "sonnet" => 0.08,
                    "haiku"  => 0.02,
                    _        => 0.05,
                };
                let tokens = (total_tokens as f64 * share) as u64;
                let cost = calc_session_cost(model, tokens, (tokens as f64 * output_ratio(model)) as u64);
                println!("{:<24} {:<10} {:>10}",
                    cyan(agent),
                    dim(model),
                    yellow(&format!("${:.4}", cost)));
            }
        }

        CostCmd::SetBudget { amount } => {
            let budget = Budget { monthly: amount };
            save_budget(&budget)?;
            println!("{} Monthly budget set to ${:.2}", green("[OK]"), amount);
        }
    }
    Ok(())
}
