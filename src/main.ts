/**
 * Main entry point for APEX SuperSonic Core
 */

import { OpportunityDetector } from './core/opportunityDetector.js';
import { Config } from './config.js';

async function main() {
    console.log('🚀 APEX SuperSonic Core - Starting...');
    console.log(`Environment: ${Config.getEnvironment()}`);
    console.log(`Debug Mode: ${Config.getDebugMode()}`);
    console.log(`Dry Run: ${Config.getDryRun()}`);
    
    // Validate configuration
    const validation = Config.validateConfig();
    if (validation.warnings.length > 0) {
        console.warn('⚠️  Configuration warnings:');
        validation.warnings.forEach(warning => console.warn(`  - ${warning}`));
    }
    if (!validation.valid) {
        console.error('❌ Configuration errors:');
        validation.issues.forEach(issue => console.error(`  - ${issue}`));
        process.exit(1);
    }
    
    const detector = new OpportunityDetector();
    await detector.initialize();
    
    console.log('✅ APEX SuperSonic Core - Ready');
}

main().catch((error) => {
    console.error('❌ Fatal error:', error);
    process.exit(1);
});
