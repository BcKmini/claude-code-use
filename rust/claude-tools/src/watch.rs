use anyhow::Result;
use std::collections::HashSet;
use std::path::PathBuf;
use std::time::Duration;

use crate::colors::*;

const PRICING: &[(&str, f64, f64)] = &[
    ("opus",    15.00, 75.00),
    ("sonnet",   3.00, 15.00),
    ("haiku",    0.25,  1.25),
];

fn projects_dir() -> PathBuf {
    dirs::home_dir().unwrap().join(".claude").join("projects")
}

fn pricing(model: &str) -> (f64, f64) {
    PRICING.iter()
        .find(|(name, _, _)| model.contains(name))
        .map(|(_, i, o)| (*i, *o))
        .unwrap_or((3.00, 15.00))
}

fn calc_cost(input: u64, output: u64, model: &str) -> f64 {
    let (inp_price, out_price) = pricing(model);
    (input as f64 / 1_000_000.0 * inp_price) + (output as f64 / 1_000_000.0 * out_price)
}

fn short_model(model: &str) -> &str {
    if model.contains("opus")   { "opus"   }
    else if model.contains("sonnet") { "sonnet" }
    else if model.contains("haiku")  { "haiku"  }
    else                             { "sonnet"  }
}

#[derive(Debug, Clone)]
struct Entry {
    time: String,
    model: String,
    input: u64,
    output: u64,
    cost: f64,
}

fn scan_entries(seen: &HashSet<String>) -> (Vec<Entry>, HashSet<String>) {
    let dir = projects_dir();
    let mut entries: Vec<Entry> = Vec::new();
    let mut new_seen = seen.clone();

    if !dir.exists() {
        return (entries, new_seen);
    }
    let Ok(project_dirs) = std::fs::read_dir(&dir) else {
        return (entries, new_seen);
    };

    // Only look at today's sessions for live monitoring
    let today = chrono::Local::now().format("%Y-%m-%d").to_string();

    for pd in project_dirs.filter_map(|e| e.ok()) {
        let Ok(files) = std::fs::read_dir(pd.path()) else { continue };
        for file in files.filter_map(|e| e.ok()) {
            let path = file.path();
            if !path.extension().map(|e| e == "jsonl").unwrap_or(false) {
                continue;
            }
            let Ok(content) = std::fs::read_to_string(&path) else { continue };
            for (i, line) in content.lines().enumerate() {
                let key = format!("{}:{}", path.display(), i);
                if seen.contains(&key) {
                    continue;
                }
                let Ok(val) = serde_json::from_str::<serde_json::Value>(line) else { continue };
                let Some(usage) = val.get("usage") else { continue };
                let ts = val.get("timestamp").and_then(|t| t.as_str()).unwrap_or("");
                let Ok(dt) = chrono::DateTime::parse_from_rfc3339(ts) else { continue };
                let date = dt.format("%Y-%m-%d").to_string();
                if date != today {
                    new_seen.insert(key);
                    continue;
                }
                let time = dt.with_timezone(&chrono::Local).format("%H:%M:%S").to_string();
                let model = val.get("model")
                    .and_then(|m| m.as_str())
                    .unwrap_or("sonnet")
                    .to_string();
                let input  = usage.get("input_tokens").and_then(|v| v.as_u64()).unwrap_or(0);
                let output = usage.get("output_tokens").and_then(|v| v.as_u64()).unwrap_or(0);
                if input == 0 && output == 0 {
                    new_seen.insert(key);
                    continue;
                }
                let cost = calc_cost(input, output, &model);
                entries.push(Entry { time, model, input, output, cost });
                new_seen.insert(key);
            }
        }
    }
    (entries, new_seen)
}

fn render(all: &[Entry]) {
    // Clear screen with ANSI escape
    print!("\x1b[2J\x1b[H");

    println!("{}", bold("Claude Code — Live Cost Monitor  (Ctrl+C to exit)"));
    println!("{}", dim("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"));
    println!(" {:<8} {:<8} {:>9} {:>9}  {}",
        bold("TIME"), bold("MODEL"), bold("INPUT"), bold("OUTPUT"), bold("COST"));

    let mut total_in: u64  = 0;
    let mut total_out: u64 = 0;
    let mut total_cost: f64 = 0.0;

    if all.is_empty() {
        println!("{}", dim("  (waiting for token events...)"));
    } else {
        for e in all {
            println!(" {:<8} {:<8} {:>9} {:>9}  {}",
                dim(&e.time),
                cyan(short_model(&e.model)),
                format!("{:>7}", format_num(e.input)),
                format!("{:>7}", format_num(e.output)),
                green(&format!("${:.4}", e.cost)),
            );
            total_in   += e.input;
            total_out  += e.output;
            total_cost += e.cost;
        }
    }

    println!("{}", dim("─────────────────────────────────────────────────"));
    println!(" {:<8} {:<8} {:>9} {:>9}  {}",
        bold("TOTAL"), "",
        format!("{:>7}", format_num(total_in)),
        format!("{:>7}", format_num(total_out)),
        bold(&green(&format!("${:.4}", total_cost))),
    );
}

fn format_num(n: u64) -> String {
    if n == 0 { return "—".to_string(); }
    let s = n.to_string();
    let mut result = String::new();
    for (i, c) in s.chars().rev().enumerate() {
        if i > 0 && i % 3 == 0 { result.push(','); }
        result.push(c);
    }
    result.chars().rev().collect()
}

pub fn run(interval: u64) -> Result<()> {
    let mut all: Vec<Entry> = Vec::new();
    let mut seen: HashSet<String> = HashSet::new();

    println!("{}", bold("Starting live cost monitor... (Ctrl+C to exit)"));

    loop {
        let (new_entries, new_seen) = scan_entries(&seen);
        seen = new_seen;
        all.extend(new_entries);
        // keep chronological order
        all.sort_by(|a, b| a.time.cmp(&b.time));

        render(&all);

        std::thread::sleep(Duration::from_secs(interval));
    }
}
