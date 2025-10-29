"""Whale Tracker for Large Transaction Monitoring.

This module tracks and analyzes large transactions (whale movements)
to identify significant market participants and potential market impacts.
"""

from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class WhaleTracker:
    """
    Tracks whale transactions and analyzes their market impact.
    
    Monitors large transactions to:
    - Identify whale wallets
    - Detect accumulation/distribution patterns
    - Predict potential price movements
    """
    
    def __init__(
        self,
        whale_threshold: float = 100000.0,
        tracking_window_hours: int = 24
    ):
        """
        Initialize the whale tracker.
        
        Args:
            whale_threshold: Minimum transaction value (USD) to classify as whale
            tracking_window_hours: Hours to track whale activity
        """
        self.whale_threshold = whale_threshold
        self.tracking_window = timedelta(hours=tracking_window_hours)
        
        # Whale data
        self.whale_wallets = {}
        self.whale_transactions = []
        self.accumulation_patterns = defaultdict(list)
        
        # Alert system
        self.alerts = []
        
        logger.info("Whale Tracker initialized")
    
    def track_transaction(
        self,
        tx_hash: str,
        wallet_address: str,
        token: str,
        amount: float,
        value_usd: float,
        tx_type: str,  # 'buy' or 'sell'
        timestamp: Optional[datetime] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Track a transaction and classify if it's a whale transaction.
        
        Args:
            tx_hash: Transaction hash
            wallet_address: Wallet address
            token: Token symbol
            amount: Token amount
            value_usd: USD value
            tx_type: Transaction type
            timestamp: Transaction timestamp
            
        Returns:
            Whale alert if transaction qualifies
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        transaction = {
            'tx_hash': tx_hash,
            'wallet': wallet_address,
            'token': token,
            'amount': amount,
            'value_usd': value_usd,
            'type': tx_type,
            'timestamp': timestamp
        }
        
        # Check if whale transaction
        if value_usd >= self.whale_threshold:
            self.whale_transactions.append(transaction)
            
            # Update whale wallet info
            if wallet_address not in self.whale_wallets:
                self.whale_wallets[wallet_address] = {
                    'first_seen': timestamp,
                    'total_volume': 0.0,
                    'transaction_count': 0,
                    'tokens': set()
                }
            
            wallet_info = self.whale_wallets[wallet_address]
            wallet_info['total_volume'] += value_usd
            wallet_info['transaction_count'] += 1
            wallet_info['tokens'].add(token)
            wallet_info['last_seen'] = timestamp
            
            # Track accumulation pattern
            self.accumulation_patterns[wallet_address].append(transaction)
            
            # Generate alert
            alert = self._generate_whale_alert(transaction)
            self.alerts.append(alert)
            
            logger.info(
                f"Whale transaction detected: {tx_type.upper()} "
                f"{amount:.2f} {token} (${value_usd:,.0f})"
            )
            
            return alert
        
        return None
    
    def get_whale_sentiment(self, token: str) -> Dict[str, Any]:
        """
        Analyze whale sentiment for a token.
        
        Args:
            token: Token symbol
            
        Returns:
            Sentiment analysis
        """
        # Get recent whale transactions for this token
        cutoff_time = datetime.now() - self.tracking_window
        recent_txs = [
            tx for tx in self.whale_transactions
            if tx['token'] == token and tx['timestamp'] >= cutoff_time
        ]
        
        if not recent_txs:
            return {
                'sentiment': 'neutral',
                'confidence': 0.0,
                'buy_volume': 0.0,
                'sell_volume': 0.0,
                'net_flow': 0.0
            }
        
        # Calculate volumes
        buy_volume = sum(tx['value_usd'] for tx in recent_txs if tx['type'] == 'buy')
        sell_volume = sum(tx['value_usd'] for tx in recent_txs if tx['type'] == 'sell')
        net_flow = buy_volume - sell_volume
        
        # Determine sentiment
        total_volume = buy_volume + sell_volume
        if total_volume == 0:
            sentiment = 'neutral'
            confidence = 0.0
        else:
            buy_ratio = buy_volume / total_volume
            
            if buy_ratio > 0.6:
                sentiment = 'bullish'
            elif buy_ratio < 0.4:
                sentiment = 'bearish'
            else:
                sentiment = 'neutral'
            
            confidence = abs(buy_ratio - 0.5) * 2  # 0 to 1 scale
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'buy_volume': buy_volume,
            'sell_volume': sell_volume,
            'net_flow': net_flow,
            'transaction_count': len(recent_txs),
            'unique_whales': len(set(tx['wallet'] for tx in recent_txs))
        }
    
    def identify_accumulation(
        self,
        wallet_address: str,
        min_transactions: int = 5
    ) -> Dict[str, Any]:
        """
        Identify if a whale is accumulating a token.
        
        Args:
            wallet_address: Whale wallet address
            min_transactions: Minimum transactions to analyze
            
        Returns:
            Accumulation analysis
        """
        patterns = self.accumulation_patterns.get(wallet_address, [])
        
        if len(patterns) < min_transactions:
            return {
                'is_accumulating': False,
                'confidence': 0.0,
                'pattern': 'insufficient_data'
            }
        
        # Analyze recent transactions
        recent = patterns[-min_transactions:]
        buy_count = sum(1 for tx in recent if tx['type'] == 'buy')
        
        # Calculate accumulation metrics
        buy_ratio = buy_count / len(recent)
        
        # Check for consistent buying
        is_accumulating = buy_ratio > 0.7
        
        # Calculate total accumulated
        total_buy_value = sum(tx['value_usd'] for tx in recent if tx['type'] == 'buy')
        total_sell_value = sum(tx['value_usd'] for tx in recent if tx['type'] == 'sell')
        
        return {
            'is_accumulating': is_accumulating,
            'confidence': buy_ratio,
            'pattern': 'accumulation' if is_accumulating else 'distribution',
            'buy_ratio': buy_ratio,
            'net_position_change': total_buy_value - total_sell_value,
            'transaction_count': len(recent)
        }
    
    def get_top_whales(
        self,
        token: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get top whale wallets by volume.
        
        Args:
            token: Optional token filter
            limit: Number of whales to return
            
        Returns:
            List of top whales
        """
        # Filter whales by token if specified
        if token:
            filtered_whales = {
                addr: info for addr, info in self.whale_wallets.items()
                if token in info.get('tokens', set())
            }
        else:
            filtered_whales = self.whale_wallets
        
        # Sort by total volume
        sorted_whales = sorted(
            filtered_whales.items(),
            key=lambda x: x[1]['total_volume'],
            reverse=True
        )
        
        # Format results
        top_whales = []
        for addr, info in sorted_whales[:limit]:
            whale_data = {
                'address': addr,
                'total_volume': info['total_volume'],
                'transaction_count': info['transaction_count'],
                'tokens_traded': list(info.get('tokens', set())),
                'first_seen': info['first_seen'].isoformat(),
                'last_seen': info.get('last_seen', info['first_seen']).isoformat()
            }
            top_whales.append(whale_data)
        
        return top_whales
    
    def predict_impact(
        self,
        token: str,
        whale_transaction_value: float
    ) -> Dict[str, Any]:
        """
        Predict potential market impact of a whale transaction.
        
        Args:
            token: Token symbol
            whale_transaction_value: Size of transaction
            
        Returns:
            Impact prediction
        """
        # Get recent whale activity
        sentiment = self.get_whale_sentiment(token)
        
        # Calculate relative impact
        recent_volume = sentiment['buy_volume'] + sentiment['sell_volume']
        
        if recent_volume > 0:
            relative_size = whale_transaction_value / recent_volume
        else:
            relative_size = 1.0
        
        # Estimate price impact
        # Larger transactions relative to recent volume have more impact
        if relative_size > 0.5:
            impact_level = 'high'
            estimated_price_impact = 0.05  # 5%
        elif relative_size > 0.2:
            impact_level = 'medium'
            estimated_price_impact = 0.02  # 2%
        else:
            impact_level = 'low'
            estimated_price_impact = 0.005  # 0.5%
        
        return {
            'impact_level': impact_level,
            'estimated_price_impact': estimated_price_impact,
            'relative_size': relative_size,
            'current_sentiment': sentiment['sentiment'],
            'confidence': min(relative_size, 1.0)
        }
    
    def _generate_whale_alert(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Generate alert for whale transaction."""
        alert = {
            'type': 'whale_transaction',
            'timestamp': transaction['timestamp'].isoformat(),
            'wallet': transaction['wallet'],
            'token': transaction['token'],
            'amount': transaction['amount'],
            'value_usd': transaction['value_usd'],
            'transaction_type': transaction['type'],
            'severity': self._calculate_alert_severity(transaction['value_usd']),
            'message': self._format_alert_message(transaction)
        }
        
        return alert
    
    def _calculate_alert_severity(self, value_usd: float) -> str:
        """Calculate alert severity based on transaction value."""
        if value_usd >= 1000000:  # $1M+
            return 'critical'
        elif value_usd >= 500000:  # $500k+
            return 'high'
        elif value_usd >= 250000:  # $250k+
            return 'medium'
        else:
            return 'low'
    
    def _format_alert_message(self, transaction: Dict[str, Any]) -> str:
        """Format whale alert message."""
        return (
            f"🐋 Whale {transaction['type'].upper()}: "
            f"{transaction['amount']:.2f} {transaction['token']} "
            f"(${transaction['value_usd']:,.0f})"
        )
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent whale alerts."""
        return self.alerts[-limit:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get whale tracker statistics."""
        cutoff_time = datetime.now() - self.tracking_window
        recent_txs = [
            tx for tx in self.whale_transactions
            if tx['timestamp'] >= cutoff_time
        ]
        
        return {
            'total_whales_tracked': len(self.whale_wallets),
            'total_whale_transactions': len(self.whale_transactions),
            'recent_transactions': len(recent_txs),
            'total_volume_tracked': sum(
                info['total_volume'] for info in self.whale_wallets.values()
            ),
            'whale_threshold': self.whale_threshold,
            'tracking_window_hours': self.tracking_window.total_seconds() / 3600
        }
