"""On-Chain Analytics Module.

This module analyzes blockchain data to extract insights about
token movements, smart contract interactions, and network activity.
"""

from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class OnChainAnalytics:
    """
    Analyzes on-chain data for trading insights.
    
    Tracks:
    - Token transfers and flows
    - Smart contract interactions
    - Network activity metrics
    - Holder distribution
    - Liquidity movements
    """
    
    def __init__(self):
        """Initialize the on-chain analytics module."""
        # Data storage
        self.token_transfers = defaultdict(list)
        self.contract_interactions = defaultdict(list)
        self.holder_data = {}
        self.liquidity_events = []
        
        # Metrics cache
        self.cached_metrics = {}
        self.cache_timestamp = {}
        
        logger.info("On-Chain Analytics initialized")
    
    def track_transfer(
        self,
        token: str,
        from_address: str,
        to_address: str,
        amount: float,
        tx_hash: str,
        timestamp: Optional[datetime] = None
    ) -> None:
        """
        Track a token transfer.
        
        Args:
            token: Token symbol
            from_address: Sender address
            to_address: Receiver address
            amount: Transfer amount
            tx_hash: Transaction hash
            timestamp: Transaction timestamp
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        transfer = {
            'from': from_address,
            'to': to_address,
            'amount': amount,
            'tx_hash': tx_hash,
            'timestamp': timestamp
        }
        
        self.token_transfers[token].append(transfer)
        
        # Update holder data
        self._update_holder_data(token, from_address, to_address, amount)
    
    def track_contract_interaction(
        self,
        contract_address: str,
        function_name: str,
        caller: str,
        value: float,
        gas_used: int,
        tx_hash: str,
        timestamp: Optional[datetime] = None
    ) -> None:
        """
        Track a smart contract interaction.
        
        Args:
            contract_address: Contract address
            function_name: Function called
            caller: Address that called the function
            value: Value transferred
            gas_used: Gas consumed
            tx_hash: Transaction hash
            timestamp: Transaction timestamp
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        interaction = {
            'function': function_name,
            'caller': caller,
            'value': value,
            'gas_used': gas_used,
            'tx_hash': tx_hash,
            'timestamp': timestamp
        }
        
        self.contract_interactions[contract_address].append(interaction)
    
    def analyze_token_flow(
        self,
        token: str,
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Analyze token flow patterns.
        
        Args:
            token: Token symbol
            time_window_hours: Analysis time window
            
        Returns:
            Flow analysis
        """
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        
        # Get recent transfers
        recent_transfers = [
            t for t in self.token_transfers[token]
            if t['timestamp'] >= cutoff_time
        ]
        
        if not recent_transfers:
            return {
                'token': token,
                'total_volume': 0.0,
                'transfer_count': 0,
                'net_flow': 0.0,
                'top_receivers': [],
                'top_senders': []
            }
        
        # Calculate metrics
        total_volume = sum(t['amount'] for t in recent_transfers)
        
        # Aggregate by address
        sender_volumes = defaultdict(float)
        receiver_volumes = defaultdict(float)
        
        for transfer in recent_transfers:
            sender_volumes[transfer['from']] += transfer['amount']
            receiver_volumes[transfer['to']] += transfer['amount']
        
        # Top senders and receivers
        top_senders = sorted(
            sender_volumes.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        top_receivers = sorted(
            receiver_volumes.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            'token': token,
            'total_volume': total_volume,
            'transfer_count': len(recent_transfers),
            'unique_senders': len(sender_volumes),
            'unique_receivers': len(receiver_volumes),
            'top_senders': [{'address': addr, 'volume': vol} for addr, vol in top_senders],
            'top_receivers': [{'address': addr, 'volume': vol} for addr, vol in top_receivers],
            'average_transfer_size': total_volume / len(recent_transfers)
        }
    
    def analyze_holder_distribution(
        self,
        token: str
    ) -> Dict[str, Any]:
        """
        Analyze token holder distribution.
        
        Args:
            token: Token symbol
            
        Returns:
            Holder distribution analysis
        """
        if token not in self.holder_data:
            return {
                'token': token,
                'total_holders': 0,
                'concentration': 0.0,
                'top_10_percentage': 0.0
            }
        
        holders = self.holder_data[token]
        
        # Sort by balance
        sorted_holders = sorted(
            holders.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        total_supply = sum(holders.values())
        
        if total_supply == 0:
            return {
                'token': token,
                'total_holders': len(holders),
                'concentration': 0.0,
                'top_10_percentage': 0.0
            }
        
        # Calculate concentration
        top_10_balance = sum(balance for _, balance in sorted_holders[:10])
        top_10_pct = (top_10_balance / total_supply) * 100
        
        # Gini coefficient approximation
        concentration = self._calculate_gini(sorted_holders, total_supply)
        
        return {
            'token': token,
            'total_holders': len(holders),
            'total_supply': total_supply,
            'concentration': concentration,
            'top_10_percentage': top_10_pct,
            'top_holders': [
                {'address': addr, 'balance': bal, 'percentage': (bal/total_supply)*100}
                for addr, bal in sorted_holders[:10]
            ]
        }
    
    def detect_liquidity_events(
        self,
        token: str,
        min_value: float = 10000.0
    ) -> List[Dict[str, Any]]:
        """
        Detect significant liquidity events.
        
        Args:
            token: Token symbol
            min_value: Minimum value to consider significant
            
        Returns:
            List of liquidity events
        """
        events = []
        
        # Check recent transfers for large movements to/from DEX contracts
        dex_patterns = ['0xdex', '0xuniswap', '0xsushiswap']  # Simplified patterns
        
        recent_transfers = self.token_transfers[token][-100:]  # Last 100 transfers
        
        for transfer in recent_transfers:
            # Check if involves DEX
            is_dex_related = any(
                pattern in transfer['from'].lower() or pattern in transfer['to'].lower()
                for pattern in dex_patterns
            )
            
            if is_dex_related and transfer['amount'] * 100 >= min_value:  # Rough value estimation
                event_type = 'liquidity_add' if '0xdex' in transfer['to'].lower() else 'liquidity_remove'
                
                events.append({
                    'type': event_type,
                    'token': token,
                    'amount': transfer['amount'],
                    'timestamp': transfer['timestamp'].isoformat(),
                    'tx_hash': transfer['tx_hash']
                })
        
        return events
    
    def get_network_activity(
        self,
        contract_address: str,
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get network activity metrics for a contract.
        
        Args:
            contract_address: Contract address
            time_window_hours: Time window for analysis
            
        Returns:
            Activity metrics
        """
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        
        # Get recent interactions
        recent_interactions = [
            i for i in self.contract_interactions[contract_address]
            if i['timestamp'] >= cutoff_time
        ]
        
        if not recent_interactions:
            return {
                'contract': contract_address,
                'total_interactions': 0,
                'unique_users': 0,
                'total_value': 0.0,
                'total_gas_used': 0
            }
        
        # Calculate metrics
        unique_users = len(set(i['caller'] for i in recent_interactions))
        total_value = sum(i['value'] for i in recent_interactions)
        total_gas = sum(i['gas_used'] for i in recent_interactions)
        
        # Function call distribution
        function_counts = defaultdict(int)
        for interaction in recent_interactions:
            function_counts[interaction['function']] += 1
        
        return {
            'contract': contract_address,
            'total_interactions': len(recent_interactions),
            'unique_users': unique_users,
            'total_value': total_value,
            'total_gas_used': total_gas,
            'average_gas_per_tx': total_gas / len(recent_interactions),
            'function_distribution': dict(function_counts),
            'most_called_function': max(function_counts.items(), key=lambda x: x[1])[0] if function_counts else None
        }
    
    def calculate_velocity(
        self,
        token: str,
        time_window_hours: int = 24
    ) -> float:
        """
        Calculate token velocity (transaction volume / supply).
        
        Args:
            token: Token symbol
            time_window_hours: Time window
            
        Returns:
            Velocity metric
        """
        flow_data = self.analyze_token_flow(token, time_window_hours)
        holder_data = self.analyze_holder_distribution(token)
        
        volume = flow_data['total_volume']
        supply = holder_data['total_supply']
        
        if supply == 0:
            return 0.0
        
        # Velocity = Volume / Supply
        velocity = volume / supply
        return velocity
    
    def _update_holder_data(
        self,
        token: str,
        from_address: str,
        to_address: str,
        amount: float
    ) -> None:
        """Update holder balances."""
        if token not in self.holder_data:
            self.holder_data[token] = {}
        
        holders = self.holder_data[token]
        
        # Update sender balance
        if from_address in holders:
            holders[from_address] = max(0, holders[from_address] - amount)
        
        # Update receiver balance
        if to_address not in holders:
            holders[to_address] = 0
        holders[to_address] += amount
        
        # Clean up zero balances
        if from_address in holders and holders[from_address] == 0:
            del holders[from_address]
    
    def _calculate_gini(
        self,
        sorted_holders: List[tuple],
        total_supply: float
    ) -> float:
        """Calculate Gini coefficient for holder concentration."""
        if not sorted_holders or total_supply == 0:
            return 0.0
        
        n = len(sorted_holders)
        cumulative = 0
        gini_sum = 0
        
        for i, (_, balance) in enumerate(sorted_holders):
            cumulative += balance
            gini_sum += (2 * (i + 1) - n - 1) * balance
        
        gini = gini_sum / (n * total_supply)
        return abs(gini)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get on-chain analytics statistics."""
        return {
            'tokens_tracked': len(self.token_transfers),
            'total_transfers_tracked': sum(len(transfers) for transfers in self.token_transfers.values()),
            'contracts_monitored': len(self.contract_interactions),
            'total_interactions': sum(len(interactions) for interactions in self.contract_interactions.values())
        }
