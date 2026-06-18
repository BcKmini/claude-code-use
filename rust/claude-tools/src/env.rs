use anyhow::Result;
use std::path::PathBuf;

use crate::colors::{bold, cyan, dim, green, red, yellow};

pub fn run() -> Result<()> {
    println!("\n{}", bold("Claude Code Environment"));
    println!();

    check_api_key();
    check_claude_home();
    check_agents();
    check_commands();
    check_handoffs();
    check_sessions();

    println!();
    Ok(())
}

fn claude_home() -> PathBuf {
    dirs::home_dir()
        .unwrap_or_else(|| PathBuf::from("."))
        .join(".claude")
}

fn check_api_key() {
    let key = std::env::var("ANTHROPIC_API_KEY").unwrap_or_default();
    if key.is_empty() {
        println!("  {} ANTHROPIC_API_KEY   not set", red("✗"));
    } else {
        let prefix = &key[..8.min(key.len())];
        let suffix = &key[key.len().saturating_sub(4)..];
        println!(
            "  {} ANTHROPIC_API_KEY   {}",
            green("✓"),
            dim(&format!("{prefix}…{suffix}"))
        );
    }
}

fn check_claude_home() {
    let home = claude_home();
    if home.exists() {
        println!("  {} ~/.claude/           exists", green("✓"));
    } else {
        println!(
            "  {} ~/.claude/           missing — run: {}",
            red("✗"),
            dim("claude --help")
        );
    }
}

fn check_agents() {
    let agents_dir = claude_home().join("agents");
    match std::fs::read_dir(&agents_dir) {
        Ok(entries) => {
            let count = entries.filter_map(|e| e.ok()).count();
            let marker = if count >= 5 {
                green("✓")
            } else {
                yellow("!")
            };
            println!(
                "  {} ~/.claude/agents/    {} agents installed",
                marker, count
            );
        }
        Err(_) => {
            println!(
                "  {} ~/.claude/agents/    not found — run: {}",
                yellow("–"),
                dim("make install-agents")
            );
        }
    }
}

fn check_commands() {
    let cmd_dir = claude_home().join("commands");
    match std::fs::read_dir(&cmd_dir) {
        Ok(entries) => {
            let names: Vec<String> = entries
                .filter_map(|e| e.ok())
                .filter_map(|e| {
                    let p = e.path();
                    if p.extension().map(|x| x == "md").unwrap_or(false) {
                        p.file_stem().and_then(|s| s.to_str()).map(String::from)
                    } else {
                        None
                    }
                })
                .collect();
            println!(
                "  {} ~/.claude/commands/  {} commands: {}",
                green("✓"),
                names.len(),
                dim(&names.join(", "))
            );
        }
        Err(_) => {
            println!(
                "  {} ~/.claude/commands/  not found — run: {}",
                yellow("–"),
                dim("make install-commands")
            );
        }
    }
}

fn check_handoffs() {
    let dir = claude_home().join("handoffs");
    match std::fs::read_dir(&dir) {
        Ok(entries) => {
            let mut files: Vec<_> = entries
                .filter_map(|e| e.ok())
                .filter(|e| e.path().extension().map(|x| x == "md").unwrap_or(false))
                .collect();
            files.sort_by_key(|e| {
                e.metadata()
                    .and_then(|m| m.modified())
                    .unwrap_or(std::time::SystemTime::UNIX_EPOCH)
            });
            if let Some(latest) = files.last() {
                println!(
                    "  {} handoffs             {} saved, latest: {}",
                    green("✓"),
                    files.len(),
                    dim(&latest.file_name().to_string_lossy())
                );
            } else {
                println!("  {} handoffs             none saved yet", cyan("–"));
            }
        }
        Err(_) => {
            println!("  {} handoffs             none saved yet", cyan("–"));
        }
    }
}

fn check_sessions() {
    let projects_dir = claude_home().join("projects");
    match std::fs::read_dir(&projects_dir) {
        Ok(entries) => {
            let project_dirs: Vec<_> = entries
                .filter_map(|e| e.ok())
                .filter(|e| e.path().is_dir())
                .collect();
            let mut session_count = 0usize;
            for dir in &project_dirs {
                if let Ok(files) = std::fs::read_dir(dir.path()) {
                    session_count += files
                        .filter_map(|e| e.ok())
                        .filter(|e| e.path().extension().map(|x| x == "jsonl").unwrap_or(false))
                        .count();
                }
            }
            println!(
                "  {} sessions             {} projects, {} session files",
                green("✓"),
                project_dirs.len(),
                session_count
            );
        }
        Err(_) => {
            println!("  {} sessions             no session data found", cyan("–"));
        }
    }
}
