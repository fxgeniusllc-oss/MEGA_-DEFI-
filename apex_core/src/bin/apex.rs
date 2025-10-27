//! APEX Core Main Binary
//!
//! Entry point for the APEX SuperSonic Core system

use apex_core::ApexCore;
use anyhow::Result;

fn main() -> Result<()> {
    // Initialize tracing
    tracing_subscriber::fmt::init();

    println!("🚀 APEX SuperSonic Core - Starting...");
    
    let mut core = ApexCore::new();
    core.initialize()?;
    
    println!("✅ APEX SuperSonic Core - Ready");
    println!("📊 All quad engines initialized successfully");
    
    Ok(())
}
