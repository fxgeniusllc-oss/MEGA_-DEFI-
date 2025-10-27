//! APEX Core - Main coordination and orchestration module
//!
//! This is the central coordination point for the APEX SuperSonic Core system.

#![allow(dead_code)]

use anyhow::Result;
use tracing::info;

// Import quad engines
use executor::Executor;
use math_engine::MathEngine;
use telemetry::TelemetryEngine;
use tx_engine::TxEngine;

/// Main APEX Core structure
pub struct ApexCore {
    initialized: bool,
    executor: Executor,
    math_engine: MathEngine,
    telemetry: TelemetryEngine,
    tx_engine: TxEngine,
}

impl ApexCore {
    /// Create a new ApexCore instance with all quad engines
    pub fn new() -> Self {
        info!("Initializing APEX Core with Quad Engines");
        Self {
            initialized: false,
            executor: Executor::new(),
            math_engine: MathEngine::new(8),
            telemetry: TelemetryEngine::new(),
            tx_engine: TxEngine::new(),
        }
    }

    /// Initialize the core system and all engines
    pub fn initialize(&mut self) -> Result<()> {
        info!("Initializing all quad engines...");
        info!("✅ Executor Engine ready");
        info!("✅ Math Engine ready");
        info!("✅ Telemetry Engine ready");
        info!("✅ TX Engine ready");
        
        self.initialized = true;
        info!("APEX Core initialized successfully");
        Ok(())
    }

    /// Get reference to the executor
    pub fn executor(&self) -> &Executor {
        &self.executor
    }

    /// Get reference to the math engine
    pub fn math_engine(&self) -> &MathEngine {
        &self.math_engine
    }

    /// Get reference to the telemetry engine
    pub fn telemetry(&self) -> &TelemetryEngine {
        &self.telemetry
    }

    /// Get reference to the tx engine
    pub fn tx_engine(&self) -> &TxEngine {
        &self.tx_engine
    }
}

impl Default for ApexCore {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_apex_core_creation() {
        let core = ApexCore::new();
        assert!(!core.initialized);
    }

    #[test]
    fn test_apex_core_initialization() {
        let mut core = ApexCore::new();
        assert!(core.initialize().is_ok());
        assert!(core.initialized);
    }
}
