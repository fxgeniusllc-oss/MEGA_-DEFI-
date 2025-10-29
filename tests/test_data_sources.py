"""Tests for Data Source Components."""

import unittest
from datetime import datetime, timedelta

from mega_defi.data_sources import (
    MarketDataAggregator,
    WhaleTracker,
    SentimentAnalyzer,
    NewsProcessor,
    OnChainAnalytics
)


class TestMarketDataAggregator(unittest.TestCase):
    """Test cases for Market Data Aggregator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.aggregator = MarketDataAggregator()
    
    def test_initialization(self):
        """Test aggregator initialization."""
        self.assertEqual(len(self.aggregator.dex_connections), 0)
        self.assertIn('uniswap_v3', self.aggregator.supported_dexs)
        self.assertIn('sushiswap', self.aggregator.supported_dexs)
    
    def test_register_dex(self):
        """Test DEX registration."""
        self.aggregator.register_dex('uniswap_v3', {'rpc': 'https://test.rpc'})
        
        self.assertIn('uniswap_v3', self.aggregator.dex_connections)
    
    def test_update_and_get_aggregated_price(self):
        """Test price aggregation."""
        token_pair = 'ETH/USDC'
        
        # Update from multiple DEXs
        self.aggregator.update_market_data(token_pair, 'uniswap_v3', 2000, 100000, {})
        self.aggregator.update_market_data(token_pair, 'sushiswap', 2005, 80000, {})
        
        # Get aggregated price
        result = self.aggregator.get_aggregated_price(token_pair, method='mean')
        
        self.assertGreater(result['price'], 0)
        self.assertEqual(result['source_count'], 2)
        self.assertGreaterEqual(result['confidence'], 0)
    
    def test_get_liquidity_depth(self):
        """Test liquidity depth aggregation."""
        token_pair = 'ETH/USDC'
        
        self.aggregator.update_market_data(
            token_pair, 'uniswap_v3', 2000, 100000,
            {'bid_liquidity': 50000, 'ask_liquidity': 60000}
        )
        
        liquidity = self.aggregator.get_liquidity_depth(token_pair)
        
        self.assertEqual(liquidity['token_pair'], token_pair)
        self.assertGreaterEqual(liquidity['total_liquidity'], 0)
    
    def test_identify_arbitrage_opportunities(self):
        """Test arbitrage opportunity detection."""
        token_pair = 'ETH/USDC'
        
        # Create price difference
        self.aggregator.update_market_data(token_pair, 'uniswap_v3', 2000, 100000, {})
        self.aggregator.update_market_data(token_pair, 'sushiswap', 2020, 80000, {})
        
        opportunities = self.aggregator.identify_arbitrage_opportunities(
            token_pair,
            min_profit_threshold=0.005
        )
        
        self.assertIsInstance(opportunities, list)
        if opportunities:
            self.assertIn('profit_percentage', opportunities[0])
    
    def test_statistics(self):
        """Test statistics retrieval."""
        stats = self.aggregator.get_statistics()
        
        self.assertIn('connected_dexs', stats)
        self.assertIn('tracked_pairs', stats)
        self.assertIn('supported_dexs', stats)


class TestWhaleTracker(unittest.TestCase):
    """Test cases for Whale Tracker."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tracker = WhaleTracker(whale_threshold=100000.0)
    
    def test_initialization(self):
        """Test tracker initialization."""
        self.assertEqual(self.tracker.whale_threshold, 100000.0)
        self.assertEqual(len(self.tracker.whale_wallets), 0)
    
    def test_track_whale_transaction(self):
        """Test whale transaction tracking."""
        alert = self.tracker.track_transaction(
            tx_hash='0x123',
            wallet_address='0xwhale1',
            token='ETH',
            amount=100,
            value_usd=200000,
            tx_type='buy'
        )
        
        self.assertIsNotNone(alert)
        self.assertEqual(alert['type'], 'whale_transaction')
        self.assertEqual(alert['token'], 'ETH')
        self.assertIn('0xwhale1', self.tracker.whale_wallets)
    
    def test_track_non_whale_transaction(self):
        """Test non-whale transaction (below threshold)."""
        alert = self.tracker.track_transaction(
            tx_hash='0x456',
            wallet_address='0xsmall',
            token='ETH',
            amount=1,
            value_usd=2000,
            tx_type='sell'
        )
        
        self.assertIsNone(alert)
    
    def test_get_whale_sentiment(self):
        """Test whale sentiment analysis."""
        # Track some whale transactions
        self.tracker.track_transaction('0x1', '0xwhale1', 'ETH', 100, 200000, 'buy')
        self.tracker.track_transaction('0x2', '0xwhale2', 'ETH', 50, 100000, 'buy')
        self.tracker.track_transaction('0x3', '0xwhale3', 'ETH', 30, 60000, 'sell')
        
        sentiment = self.tracker.get_whale_sentiment('ETH')
        
        self.assertIn('sentiment', sentiment)
        self.assertIn('buy_volume', sentiment)
        self.assertIn('sell_volume', sentiment)
        self.assertIn(sentiment['sentiment'], ['bullish', 'bearish', 'neutral'])
    
    def test_identify_accumulation(self):
        """Test accumulation pattern identification."""
        wallet = '0xwhale1'
        
        # Track multiple buys
        for i in range(6):
            self.tracker.track_transaction(
                f'0x{i}', wallet, 'ETH', 10, 120000, 'buy'
            )
        
        accumulation = self.tracker.identify_accumulation(wallet, min_transactions=5)
        
        self.assertIn('is_accumulating', accumulation)
        self.assertIn('confidence', accumulation)
    
    def test_get_top_whales(self):
        """Test top whales retrieval."""
        # Track transactions from multiple whales
        self.tracker.track_transaction('0x1', '0xwhale1', 'ETH', 100, 500000, 'buy')
        self.tracker.track_transaction('0x2', '0xwhale2', 'ETH', 50, 300000, 'buy')
        
        top_whales = self.tracker.get_top_whales(limit=2)
        
        self.assertLessEqual(len(top_whales), 2)
        if top_whales:
            self.assertIn('address', top_whales[0])
            self.assertIn('total_volume', top_whales[0])
    
    def test_predict_impact(self):
        """Test market impact prediction."""
        # Track some baseline activity
        self.tracker.track_transaction('0x1', '0xwhale1', 'ETH', 100, 200000, 'buy')
        
        impact = self.tracker.predict_impact('ETH', 500000)
        
        self.assertIn('impact_level', impact)
        self.assertIn('estimated_price_impact', impact)
        self.assertIn(impact['impact_level'], ['low', 'medium', 'high'])


class TestSentimentAnalyzer(unittest.TestCase):
    """Test cases for Sentiment Analyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = SentimentAnalyzer()
    
    def test_initialization(self):
        """Test analyzer initialization."""
        self.assertGreater(len(self.analyzer.positive_words), 0)
        self.assertGreater(len(self.analyzer.negative_words), 0)
    
    def test_analyze_positive_text(self):
        """Test positive sentiment analysis."""
        text = "ETH is bullish! Great opportunity to buy. Moon incoming! 🚀"
        
        result = self.analyzer.analyze_text(text, 'twitter')
        
        self.assertEqual(result['sentiment'], 'positive')
        self.assertGreater(result['score'], 0)
        self.assertGreater(result['positive_indicators'], 0)
    
    def test_analyze_negative_text(self):
        """Test negative sentiment analysis."""
        text = "ETH is bearish. Time to sell. Expect a crash soon."
        
        result = self.analyzer.analyze_text(text, 'twitter')
        
        self.assertEqual(result['sentiment'], 'negative')
        self.assertLess(result['score'], 0)
        self.assertGreater(result['negative_indicators'], 0)
    
    def test_analyze_neutral_text(self):
        """Test neutral sentiment analysis."""
        text = "ETH price is currently at $2000."
        
        result = self.analyzer.analyze_text(text, 'twitter')
        
        self.assertEqual(result['sentiment'], 'neutral')
    
    def test_track_post(self):
        """Test post tracking."""
        result = self.analyzer.track_post(
            text="$ETH looking strong! 🚀",
            author='trader123',
            source='twitter',
            token='ETH'
        )
        
        self.assertIn('sentiment', result)
        self.assertIn('author', result)
        self.assertIn('ETH', self.analyzer.sentiment_history)
    
    def test_analyze_token_sentiment(self):
        """Test token sentiment aggregation."""
        # Track multiple posts
        self.analyzer.track_post("$ETH bullish!", 'user1', 'twitter', 'ETH')
        self.analyzer.track_post("$ETH to the moon!", 'user2', 'twitter', 'ETH')
        
        sentiment = self.analyzer.analyze_token_sentiment('ETH')
        
        self.assertIn('sentiment', sentiment)
        self.assertIn('score', sentiment)
        self.assertIn('sample_size', sentiment)
        self.assertGreater(sentiment['sample_size'], 0)
    
    def test_get_trending_tokens(self):
        """Test trending tokens detection."""
        # Track posts for multiple tokens
        for i in range(10):
            self.analyzer.track_post(f"$ETH post {i}", f'user{i}', 'twitter', 'ETH')
        
        trending = self.analyzer.get_trending_tokens(limit=5)
        
        self.assertIsInstance(trending, list)
        if trending:
            self.assertIn('token', trending[0])
            self.assertIn('mentions', trending[0])


class TestNewsProcessor(unittest.TestCase):
    """Test cases for News Processor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = NewsProcessor()
    
    def test_initialization(self):
        """Test processor initialization."""
        self.assertGreater(len(self.processor.news_categories), 0)
        self.assertIn('listing', self.processor.news_categories)
    
    def test_process_positive_article(self):
        """Test processing positive news."""
        article = self.processor.process_article(
            title="ETH Listed on Major Exchange",
            content="Ethereum has been listed on the world's largest exchange.",
            source="coindesk",
            tokens=['ETH']
        )
        
        self.assertEqual(article['tokens'], ['ETH'])
        self.assertIn('sentiment', article)
        self.assertIn('impact_score', article)
        self.assertGreater(article['impact_score'], 0)
    
    def test_process_negative_article(self):
        """Test processing negative news."""
        article = self.processor.process_article(
            title="Protocol Suffers Major Hack",
            content="A DeFi protocol has been exploited for $10M.",
            source="cointelegraph",
            tokens=['DEFI']
        )
        
        self.assertIn('sentiment', article)
        self.assertEqual(article['category'], 'hack')
    
    def test_get_token_news_sentiment(self):
        """Test token news sentiment aggregation."""
        # Process multiple articles
        self.processor.process_article(
            "ETH Partnership Announced",
            "Ethereum partners with major company.",
            "coindesk",
            ['ETH']
        )
        
        sentiment = self.processor.get_token_news_sentiment('ETH')
        
        self.assertIn('sentiment', sentiment)
        self.assertIn('news_count', sentiment)
        self.assertEqual(sentiment['token'], 'ETH')
    
    def test_detect_market_events(self):
        """Test market event detection."""
        # Process high-impact news
        self.processor.process_article(
            "Major Exchange Hack",
            "Exchange hacked for $100M",
            "reuters",
            ['BTC', 'ETH']
        )
        
        events = self.processor.detect_market_events(time_window_hours=24)
        
        self.assertIsInstance(events, list)
    
    def test_get_breaking_news(self):
        """Test breaking news retrieval."""
        self.processor.process_article(
            "Breaking: New Development",
            "Latest news content",
            "coindesk",
            ['ETH']
        )
        
        breaking = self.processor.get_breaking_news(limit=5)
        
        self.assertIsInstance(breaking, list)
        self.assertLessEqual(len(breaking), 5)


class TestOnChainAnalytics(unittest.TestCase):
    """Test cases for On-Chain Analytics."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analytics = OnChainAnalytics()
    
    def test_initialization(self):
        """Test analytics initialization."""
        self.assertEqual(len(self.analytics.token_transfers), 0)
        self.assertEqual(len(self.analytics.holder_data), 0)
    
    def test_track_transfer(self):
        """Test transfer tracking."""
        self.analytics.track_transfer(
            token='ETH',
            from_address='0xsender',
            to_address='0xreceiver',
            amount=10.0,
            tx_hash='0x123'
        )
        
        self.assertIn('ETH', self.analytics.token_transfers)
        self.assertEqual(len(self.analytics.token_transfers['ETH']), 1)
    
    def test_track_contract_interaction(self):
        """Test contract interaction tracking."""
        self.analytics.track_contract_interaction(
            contract_address='0xcontract',
            function_name='swap',
            caller='0xuser',
            value=1000.0,
            gas_used=100000,
            tx_hash='0x456'
        )
        
        self.assertIn('0xcontract', self.analytics.contract_interactions)
    
    def test_analyze_token_flow(self):
        """Test token flow analysis."""
        # Track multiple transfers
        for i in range(5):
            self.analytics.track_transfer(
                'ETH', f'0xsender{i}', f'0xreceiver{i}', 10.0, f'0x{i}'
            )
        
        flow = self.analytics.analyze_token_flow('ETH')
        
        self.assertIn('total_volume', flow)
        self.assertIn('transfer_count', flow)
        self.assertEqual(flow['transfer_count'], 5)
    
    def test_analyze_holder_distribution(self):
        """Test holder distribution analysis."""
        # Track transfers to build holder data
        self.analytics.track_transfer('ETH', '0xgenesis', '0xholder1', 100.0, '0x1')
        self.analytics.track_transfer('ETH', '0xgenesis', '0xholder2', 50.0, '0x2')
        
        distribution = self.analytics.analyze_holder_distribution('ETH')
        
        self.assertIn('total_holders', distribution)
        self.assertIn('concentration', distribution)
        self.assertGreater(distribution['total_holders'], 0)
    
    def test_get_network_activity(self):
        """Test network activity metrics."""
        contract = '0xcontract'
        
        # Track multiple interactions
        for i in range(3):
            self.analytics.track_contract_interaction(
                contract, 'swap', f'0xuser{i}', 1000.0, 100000, f'0x{i}'
            )
        
        activity = self.analytics.get_network_activity(contract)
        
        self.assertIn('total_interactions', activity)
        self.assertIn('unique_users', activity)
        self.assertEqual(activity['total_interactions'], 3)
    
    def test_calculate_velocity(self):
        """Test token velocity calculation."""
        # Setup holder data and transfers
        self.analytics.track_transfer('ETH', '0xgenesis', '0xholder1', 100.0, '0x1')
        self.analytics.track_transfer('ETH', '0xholder1', '0xholder2', 20.0, '0x2')
        
        velocity = self.analytics.calculate_velocity('ETH')
        
        self.assertGreaterEqual(velocity, 0.0)


if __name__ == '__main__':
    unittest.main()
