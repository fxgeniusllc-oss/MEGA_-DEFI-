/**
 * Main entry point for APEX SuperSonic Core
 */

import { OpportunityDetector } from './core/opportunityDetector.js';

async function main() {
    console.log('🚀 APEX SuperSonic Core - Starting...');
    
    const detector = new OpportunityDetector();
    await detector.initialize();
    
    console.log('✅ APEX SuperSonic Core - Ready');
}

main().catch((error) => {
    console.error('❌ Fatal error:', error);
    process.exit(1);
});
