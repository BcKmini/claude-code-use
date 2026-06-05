use anyhow::{bail, Context, Result};
use clap::Subcommand;
use regex::Regex;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::PathBuf;

use crate::colors::*;

fn snippets_file() -> PathBuf {
    dirs::home_dir().unwrap().join(".claude").join("snippets.json")
}

#[derive(Debug, Serialize, Deserialize, Default)]
struct Snippet {
    prompt: String,
    #[serde(default)]
    tags: Vec<String>,
    #[serde(default)]
    created: String,
    #[serde(default)]
    updated: String,
    #[serde(default)]
    use_count: u32,
}

fn load() -> Result<HashMap<String, Snippet>> {
    let path = snippets_file();
    if !path.exists() {
        return Ok(HashMap::new());
    }
    let text = std::fs::read_to_string(&path)?;
    let map: HashMap<String, Snippet> = serde_json::from_str(&text)
        .context("Failed to parse snippets.json")?;
    Ok(map)
}

fn save(map: &HashMap<String, Snippet>) -> Result<()> {
    let path = snippets_file();
    if let Some(parent) = path.parent() {
        std::fs::create_dir_all(parent)?;
    }
    let text = serde_json::to_string_pretty(map)?;
    std::fs::write(&path, text)?;
    Ok(())
}

fn now_str() -> String {
    chrono::Local::now().format("%Y-%m-%dT%H:%M:%S").to_string()
}

fn fill_vars(prompt: &str, vars: &[(String, String)]) -> (String, Vec<String>) {
    let re = Regex::new(r"\{\{(\w+)\}\}").unwrap();
    let var_map: HashMap<&str, &str> = vars.iter().map(|(k, v)| (k.as_str(), v.as_str())).collect();
    let mut missing = Vec::new();
    let result = re.replace_all(prompt, |caps: &regex::Captures| {
        let key = &caps[1];
        if let Some(val) = var_map.get(key) {
            val.to_string()
        } else {
            missing.push(key.to_string());
            caps[0].to_string()
        }
    });
    (result.into_owned(), missing)
}

#[derive(Subcommand)]
pub enum SnippetCmd {
    /// List all snippets
    List {
        #[arg(long)] tag: Option<String>,
    },
    /// Save a snippet
    Save {
        name: String,
        prompt: String,
        #[arg(long, value_delimiter = ',')] tags: Vec<String>,
        #[arg(long)] force: bool,
    },
    /// Print a snippet (with variable substitution)
    Run {
        name: String,
        #[arg(long, value_parser = parse_key_val)] var: Vec<(String, String)>,
        #[arg(long)] dry_run: bool,
    },
    /// Show a snippet's raw prompt
    Show { name: String },
    /// Delete a snippet
    #[command(alias = "rm")]
    Delete {
        name: String,
        #[arg(long)] force: bool,
    },
    /// Search snippets by keyword
    Search {
        query: String,
        #[arg(long)] tag: Option<String>,
    },
    /// List all tags
    Tags,
    /// Copy a snippet to a new name
    Cp {
        src: String,
        dst: String,
        #[arg(long)] force: bool,
    },
    /// Show stats
    Stats,
    /// Import snippets from a JSON file
    Import {
        file: String,
        #[arg(long)] overwrite: bool,
    },
    /// Export snippets to a JSON file
    Export {
        file: String,
        #[arg(long)] tag: Option<String>,
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

pub fn run(cmd: SnippetCmd) -> Result<()> {
    match cmd {
        SnippetCmd::Version => {
            println!("claude-tools snippet v1.0.0");
        }

        SnippetCmd::List { tag } => {
            let map = load()?;
            let mut entries: Vec<(&String, &Snippet)> = map.iter().collect();
            entries.sort_by_key(|(k, _)| k.as_str());
            if let Some(ref t) = tag {
                entries.retain(|(_, s)| s.tags.contains(t));
            }
            if entries.is_empty() {
                println!("No snippets found.");
                return Ok(());
            }
            println!("{}", bold(&format!("{:<20} {:<30} {}", "NAME", "TAGS", "VARS")));
            println!("{}", "-".repeat(60));
            let re = Regex::new(r"\{\{(\w+)\}\}").unwrap();
            for (name, snip) in &entries {
                let tags = snip.tags.join(",");
                let vars: Vec<_> = re.captures_iter(&snip.prompt)
                    .map(|c| c[1].to_string())
                    .collect::<std::collections::HashSet<_>>()
                    .into_iter()
                    .collect();
                println!("{:<20} {:<30} {}",
                    cyan(name),
                    dim(&tags),
                    yellow(&vars.join(",")));
            }
            println!("\n{} snippet(s)", entries.len());
        }

        SnippetCmd::Save { name, prompt, tags, force } => {
            let mut map = load()?;
            if map.contains_key(&name) && !force {
                bail!("Snippet '{}' already exists. Use --force to overwrite.", name);
            }
            let now = now_str();
            let existing = map.remove(&name);
            map.insert(name.clone(), Snippet {
                prompt,
                tags,
                created: existing.map(|s| s.created).unwrap_or_else(|| now.clone()),
                updated: now,
                use_count: 0,
            });
            save(&map)?;
            println!("{} Saved snippet '{}'", green("[OK]"), name);
        }

        SnippetCmd::Show { name } => {
            let map = load()?;
            match map.get(&name) {
                Some(s) => println!("{}", s.prompt),
                None => bail!("Snippet '{}' not found.", name),
            }
        }

        SnippetCmd::Run { name, var, dry_run } => {
            let mut map = load()?;
            let snip = map.get(&name).context(format!("Snippet '{}' not found.", name))?;
            let (filled, missing) = fill_vars(&snip.prompt, &var);
            if !missing.is_empty() {
                eprintln!("{} Missing variables: {}", yellow("[WARN]"), missing.join(", "));
            }
            if dry_run {
                println!("{}", dim("--- DRY RUN ---"));
                println!("{filled}");
            } else {
                println!("{filled}");
                if let Some(s) = map.get_mut(&name) {
                    s.use_count += 1;
                }
                save(&map)?;
            }
        }

        SnippetCmd::Delete { name, force } => {
            let mut map = load()?;
            if !map.contains_key(&name) {
                bail!("Snippet '{}' not found.", name);
            }
            if !force {
                bail!("Use --force to confirm deletion of '{}'.", name);
            }
            map.remove(&name);
            save(&map)?;
            println!("{} Deleted '{}'", green("[OK]"), name);
        }

        SnippetCmd::Search { query, tag } => {
            let map = load()?;
            let q = query.to_lowercase();
            let mut results: Vec<(&String, &Snippet)> = map.iter()
                .filter(|(name, snip)| {
                    let name_match = name.to_lowercase().contains(&q);
                    let prompt_match = snip.prompt.to_lowercase().contains(&q);
                    let tag_match = tag.as_ref()
                        .map(|t| snip.tags.contains(t))
                        .unwrap_or(true);
                    (name_match || prompt_match) && tag_match
                })
                .collect();
            results.sort_by_key(|(k, _)| k.as_str());
            if results.is_empty() {
                println!("No matches for '{query}'.");
            } else {
                for (name, snip) in &results {
                    let preview: String = snip.prompt.chars().take(60).collect();
                    println!("{:<20} {}", cyan(name), dim(&preview));
                }
                println!("\n{} result(s)", results.len());
            }
        }

        SnippetCmd::Tags => {
            let map = load()?;
            let mut tag_counts: HashMap<&str, usize> = HashMap::new();
            for snip in map.values() {
                for t in &snip.tags {
                    *tag_counts.entry(t.as_str()).or_default() += 1;
                }
            }
            let mut tags: Vec<_> = tag_counts.iter().collect();
            tags.sort_by(|a, b| b.1.cmp(a.1));
            for (tag, count) in tags {
                println!("{:<20} {} snippet(s)", cyan(tag), count);
            }
        }

        SnippetCmd::Cp { src, dst, force } => {
            let mut map = load()?;
            if map.contains_key(&dst) && !force {
                bail!("'{}' already exists. Use --force.", dst);
            }
            let snip = map.get(&src).context(format!("Snippet '{}' not found.", src))?;
            let new_snip = Snippet {
                prompt: snip.prompt.clone(),
                tags: snip.tags.clone(),
                created: now_str(),
                updated: now_str(),
                use_count: 0,
            };
            map.insert(dst.clone(), new_snip);
            save(&map)?;
            println!("{} Copied '{}' -> '{}'", green("[OK]"), src, dst);
        }

        SnippetCmd::Stats => {
            let map = load()?;
            let total = map.len();
            let total_uses: u32 = map.values().map(|s| s.use_count).sum();
            let mut tag_set = std::collections::HashSet::new();
            for s in map.values() {
                for t in &s.tags { tag_set.insert(t.clone()); }
            }
            println!("{}", bold("Snippet Stats"));
            println!("  Total snippets : {}", cyan(&total.to_string()));
            println!("  Total uses     : {}", cyan(&total_uses.to_string()));
            println!("  Unique tags    : {}", cyan(&tag_set.len().to_string()));
            let mut top: Vec<_> = map.iter().collect();
            top.sort_by(|a, b| b.1.use_count.cmp(&a.1.use_count));
            if let Some((name, snip)) = top.first() {
                if snip.use_count > 0 {
                    println!("  Top snippet    : {} ({} uses)", cyan(name), snip.use_count);
                }
            }
        }

        SnippetCmd::Import { file, overwrite } => {
            let text = std::fs::read_to_string(&file)
                .context(format!("Cannot read '{file}'"))?;
            let incoming: HashMap<String, Snippet> = serde_json::from_str(&text)
                .context("Invalid JSON format")?;
            let mut map = load()?;
            let mut added = 0usize;
            let mut skipped = 0usize;
            for (name, snip) in incoming {
                if map.contains_key(&name) && !overwrite {
                    skipped += 1;
                } else {
                    map.insert(name, snip);
                    added += 1;
                }
            }
            save(&map)?;
            println!("{} Imported {} snippet(s), skipped {}", green("[OK]"), added, skipped);
        }

        SnippetCmd::Export { file, tag } => {
            let map = load()?;
            let export: HashMap<&String, &Snippet> = if let Some(ref t) = tag {
                map.iter().filter(|(_, s)| s.tags.contains(t)).collect()
            } else {
                map.iter().collect()
            };
            let text = serde_json::to_string_pretty(&export)?;
            std::fs::write(&file, text)?;
            println!("{} Exported {} snippet(s) to '{}'", green("[OK]"), export.len(), file);
        }
    }
    Ok(())
}
