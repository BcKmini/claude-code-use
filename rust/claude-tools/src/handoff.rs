use anyhow::{Context, Result};
use clap::Subcommand;
use std::path::PathBuf;
use std::process::Command;

use crate::colors::*;

fn handoffs_dir() -> PathBuf {
    dirs::home_dir().unwrap().join(".claude").join("handoffs")
}

fn handoff_id() -> String {
    chrono::Local::now().format("%Y%m%d-%H%M%S").to_string()
}

fn run_git(args: &[&str]) -> Option<String> {
    Command::new("git")
        .args(args)
        .output()
        .ok()
        .filter(|o| o.status.success())
        .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_string())
}

struct GitInfo {
    branch: String,
    log: String,
    status: String,
    diff_stat: String,
    remote: String,
    root: String,
}

fn git_info() -> GitInfo {
    GitInfo {
        branch: run_git(&["rev-parse", "--abbrev-ref", "HEAD"]).unwrap_or_else(|| "unknown".into()),
        log: run_git(&["log", "--oneline", "-5"]).unwrap_or_else(|| "(no commits)".into()),
        status: run_git(&["status", "--short"]).unwrap_or_else(|| "(clean)".into()),
        diff_stat: run_git(&["diff", "--stat", "HEAD"]).unwrap_or_default(),
        remote: run_git(&["remote", "get-url", "origin"]).unwrap_or_else(|| "(none)".into()),
        root: run_git(&["rev-parse", "--show-toplevel"]).unwrap_or_else(|| {
            std::env::current_dir()
                .map(|p| p.display().to_string())
                .unwrap_or_else(|_| "(unknown)".into())
        }),
    }
}

fn find_todo() -> Option<String> {
    let mut dir = std::env::current_dir().ok()?;
    loop {
        for name in &["TODO.md", "TASKS.md"] {
            let p = dir.join(name);
            if p.exists() {
                return std::fs::read_to_string(p).ok();
            }
        }
        if !dir.pop() {
            break;
        }
    }
    None
}

fn build_doc(note: Option<&str>, git: &GitInfo) -> String {
    let id = handoff_id();
    let ts = chrono::Local::now().format("%Y-%m-%d %H:%M:%S").to_string();
    let note_str = note.unwrap_or("(none)");
    let todo = find_todo().unwrap_or_else(|| "(not found)".into());

    format!(
        "# Session Handoff — {id}\n\
        \n\
        Generated: {ts}\n\
        \n\
        ## Summary\n\
        {note_str}\n\
        \n\
        ## Git Context\n\
        \n\
        **Repository:** {root}\n\
        **Remote:** {remote}\n\
        **Branch:** `{branch}`\n\
        \n\
        ### Recent Commits\n\
        ```\n\
        {log}\n\
        ```\n\
        \n\
        ### Working Tree Status\n\
        ```\n\
        {status}\n\
        ```\n\
        \n\
        ### Diff Stat (HEAD)\n\
        ```\n\
        {diff_stat}\n\
        ```\n\
        \n\
        ## Open Tasks\n\
        {todo}\n\
        \n\
        ## Resume Prompt\n\
        \n\
        > Session handoff loaded. Branch: `{branch}`, repo: `{root}`.\n\
        > Summary: {note_str}\n\
        > Continue from where the last session left off.\n",
        id = id,
        ts = ts,
        note_str = note_str,
        root = git.root,
        remote = git.remote,
        branch = git.branch,
        log = git.log,
        status = git.status,
        diff_stat = git.diff_stat,
        todo = todo,
    )
}

#[derive(Subcommand)]
pub enum HandoffCmd {
    /// Save a handoff document for the current session
    Save {
        #[arg(long, short)]
        note: Option<String>,
    },
    /// Print the most recent handoff document to stdout
    Load {
        #[arg(long)]
        id: Option<String>,
    },
    /// List saved handoff documents
    List {
        #[arg(long, default_value = "10")]
        limit: usize,
    },
    /// Show a specific handoff document
    Show {
        #[arg(long)]
        id: Option<String>,
    },
    /// Delete old handoff documents
    Clean {
        #[arg(long, default_value = "30")]
        days: i64,
        #[arg(long)]
        force: bool,
    },
    /// Print version
    Version,
}

pub fn run(cmd: HandoffCmd) -> Result<()> {
    match cmd {
        HandoffCmd::Version => println!("claude-tools handoff v1.0.0"),

        HandoffCmd::Save { note } => {
            let dir = handoffs_dir();
            std::fs::create_dir_all(&dir)?;
            let git = git_info();
            let doc = build_doc(note.as_deref(), &git);
            let id = handoff_id();
            let path = dir.join(format!("{id}.md"));
            std::fs::write(&path, &doc)?;
            println!("{} Handoff saved: {}", green("[OK]"), id);
            println!("  File: {}", dim(&path.display().to_string()));
            println!("\nResume with: claude-tools handoff load | claude");
        }

        HandoffCmd::Load { id } => {
            let path = resolve_handoff(id)?;
            let content = std::fs::read_to_string(&path)?;
            println!("{content}");
        }

        HandoffCmd::List { limit } => {
            let entries = list_handoffs()?;
            if entries.is_empty() {
                println!("No handoff documents found.");
                return Ok(());
            }
            println!("{}", bold(&format!("{:<20}  FILE", "ID")));
            println!("{}", "-".repeat(50));
            for (id, path) in entries.iter().take(limit) {
                println!("{:<20}  {}", cyan(id), dim(&path.display().to_string()));
            }
        }

        HandoffCmd::Show { id } => {
            let path = resolve_handoff(id)?;
            let content = std::fs::read_to_string(&path)?;
            println!("{content}");
        }

        HandoffCmd::Clean { days, force } => {
            let dir = handoffs_dir();
            if !dir.exists() {
                println!("No handoffs directory found.");
                return Ok(());
            }
            let cutoff = chrono::Local::now() - chrono::Duration::days(days);
            let mut removed = 0usize;
            for entry in std::fs::read_dir(&dir)? {
                let entry = entry?;
                let path = entry.path();
                if path.extension().map(|e| e == "md").unwrap_or(false) {
                    let meta = std::fs::metadata(&path)?;
                    let modified: chrono::DateTime<chrono::Local> = meta.modified()?.into();
                    if modified < cutoff {
                        if force {
                            std::fs::remove_file(&path)?;
                            removed += 1;
                        } else {
                            println!("Would remove: {}", path.display());
                        }
                    }
                }
            }
            if force {
                println!("{} Removed {} old handoff(s)", green("[OK]"), removed);
            } else {
                println!("Run with --force to delete the listed files.");
            }
        }
    }
    Ok(())
}

fn list_handoffs() -> Result<Vec<(String, PathBuf)>> {
    let dir = handoffs_dir();
    if !dir.exists() {
        return Ok(Vec::new());
    }
    let mut entries: Vec<(String, PathBuf)> = std::fs::read_dir(&dir)?
        .filter_map(|e| e.ok())
        .filter(|e| e.path().extension().map(|x| x == "md").unwrap_or(false))
        .map(|e| {
            let path = e.path();
            let id = path
                .file_stem()
                .map(|s| s.to_string_lossy().into_owned())
                .unwrap_or_default();
            (id, path)
        })
        .collect();
    entries.sort_by(|a, b| b.0.cmp(&a.0));
    Ok(entries)
}

fn resolve_handoff(id: Option<String>) -> Result<PathBuf> {
    let dir = handoffs_dir();
    if let Some(id) = id {
        let path = dir.join(format!("{id}.md"));
        if !path.exists() {
            anyhow::bail!("Handoff '{}' not found.", id);
        }
        return Ok(path);
    }
    let entries = list_handoffs()?;
    entries
        .into_iter()
        .next()
        .map(|(_, path)| path)
        .context("No handoff documents found. Run 'handoff save' first.")
}
