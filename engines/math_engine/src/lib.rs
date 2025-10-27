//! Math Engine - Advanced mathematical computations and analysis
//!
//! Provides high-performance mathematical operations for trading strategies.

#![allow(dead_code)]

use anyhow::Result;

/// Math engine for complex calculations
pub struct MathEngine {
    precision: u32,
}

impl MathEngine {
    /// Create a new MathEngine instance
    pub fn new(precision: u32) -> Self {
        Self { precision }
    }

    /// Calculate moving average
    pub fn moving_average(&self, data: &[f64], window: usize) -> Result<Vec<f64>> {
        if data.len() < window {
            return Ok(Vec::new());
        }

        let mut result = Vec::new();
        for i in window..=data.len() {
            let sum: f64 = data[i - window..i].iter().sum();
            result.push(sum / window as f64);
        }
        Ok(result)
    }

    /// Calculate standard deviation
    pub fn std_deviation(&self, data: &[f64]) -> f64 {
        if data.is_empty() {
            return 0.0;
        }

        let mean = data.iter().sum::<f64>() / data.len() as f64;
        let variance = data.iter().map(|x| (x - mean).powi(2)).sum::<f64>() / data.len() as f64;
        variance.sqrt()
    }
}

impl Default for MathEngine {
    fn default() -> Self {
        Self::new(8)
    }
}
