mod colors;
mod snippet;
mod handoff;
mod cost;
mod watch;

use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(
    name = "claude-tools",
    version = "1.0.0",
    about = "Claude Code productivity tools: snippet manager, session handoff, cost estimator, live cost monitor",
    long_about = None
)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Personal prompt snippet manager
    Snippet {
        #[command(subcommand)]
        action: snippet::SnippetCmd,
    },
    /// Session continuity: save and load handoff documents
    Handoff {
        #[command(subcommand)]
        action: handoff::HandoffCmd,
    },
    /// Cost estimator and usage tracker
    Cost {
        #[command(subcommand)]
        action: cost::CostCmd,
    },
    /// Real-time live cost monitor (polls ~/.claude/projects/ JSONL)
    Watch {
        /// Refresh interval in seconds (default: 2)
        #[arg(long, short, default_value = "2")]
        interval: u64,
    },
}

fn main() {
    let cli = Cli::parse();
    let result = match cli.command {
        Commands::Snippet { action } => snippet::run(action),
        Commands::Handoff { action } => handoff::run(action),
        Commands::Cost    { action } => cost::run(action),
        Commands::Watch   { interval } => watch::run(interval),
    };
    if let Err(e) = result {
        eprintln!("[ERROR] {e}");
        std::process::exit(1);
    }
}
