"""Risk Manager - Portfolio protection and position sizing."""

from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class RiskLevel(str):
    """Risk level classifications."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


class RiskManager:
    """
    Advanced risk management system for DeFi trading.
    
    Manages portfolio risk, position sizing, stop losses, and
    ensures sustainable profit generation.
    """
    
    def __init__(self, max_portfolio_risk: float = 0.02, max_position_size: float = 0.1):
        """
        Initialize risk manager.
        
        Args:
            max_portfolio_risk: Maximum risk per trade as % of portfolio (default 2%)
            max_position_size: Maximum position size as % of portfolio (default 10%)
        """
        self.max_portfolio_risk = max_portfolio_risk
        self.max_position_size = max_position_size
        self.active_positions = {}
        self.portfolio_value = 0
        self.total_exposure = 0
        logger.info(f"Risk Manager initialized (max risk: {max_portfolio_risk*100}%, max position: {max_position_size*100}%)")
    
    def assess_risk(self, market_data: Dict[str, Any], strategy_type: str) -> Dict[str, Any]:
        """
        Assess risk for a potential trade.
        
        Args:
            market_data: Current market conditions
            strategy_type: Type of trading strategy
            
        Returns:
            Risk assessment including risk level, position size, and stop loss
        """
        volatility = market_data.get('volatility', 0)
        liquidity = market_data.get('liquidity', 0)
        trend_strength = market_data.get('trend_strength', 0)
        
        # Calculate risk level
        risk_level = self._calculate_risk_level(volatility, liquidity)
        
        # Calculate position size
        position_size = self._calculate_position_size(risk_level, volatility)
        
        # Calculate stop loss
        stop_loss = self._calculate_stop_loss(volatility, strategy_type)
        
        # Calculate take profit
        take_profit = self._calculate_take_profit(volatility, strategy_type)
        
        assessment = {
            'risk_level': risk_level,
            'position_size': position_size,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'max_loss': position_size * stop_loss,
            'risk_reward_ratio': take_profit / stop_loss if stop_loss > 0 else 0,
            'approved': self._approve_trade(position_size, risk_level)
        }
        
        return assessment
    
    def _calculate_risk_level(self, volatility: float, liquidity: float) -> str:
        """Determine risk level based on market conditions."""
        risk_score = 0
        
        # Volatility risk
        if volatility > 0.1:
            risk_score += 3
        elif volatility > 0.05:
            risk_score += 2
        elif volatility > 0.02:
            risk_score += 1
        
        # Liquidity risk
        if liquidity < 100000:
            risk_score += 2
        elif liquidity < 1000000:
            risk_score += 1
        
        # Classify risk level
        if risk_score >= 4:
            return RiskLevel.EXTREME
        elif risk_score >= 3:
            return RiskLevel.HIGH
        elif risk_score >= 2:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _calculate_position_size(self, risk_level: str, volatility: float) -> float:
        """Calculate optimal position size."""
        base_size = self.max_position_size
        
        # Adjust based on risk level
        if risk_level == RiskLevel.EXTREME:
            base_size *= 0.25
        elif risk_level == RiskLevel.HIGH:
            base_size *= 0.5
        elif risk_level == RiskLevel.MEDIUM:
            base_size *= 0.75
        
        # Adjust based on volatility
        if volatility > 0.1:
            base_size *= 0.5
        
        # Ensure we don't exceed maximum exposure
        remaining_capacity = 1.0 - self.total_exposure
        position_size = min(base_size, remaining_capacity)
        
        return max(0, position_size)
    
    def _calculate_stop_loss(self, volatility: float, strategy_type: str) -> float:
        """Calculate stop loss percentage."""
        base_stop = 0.02  # 2% base stop loss
        
        # Adjust based on volatility
        volatility_factor = min(volatility * 2, 0.05)
        
        # Adjust based on strategy type
        strategy_multiplier = {
            'arbitrage': 0.5,
            'trend_following': 1.5,
            'mean_reversion': 1.0,
            'momentum': 1.2,
            'liquidity_provision': 0.8
        }.get(strategy_type, 1.0)
        
        stop_loss = base_stop + volatility_factor
        stop_loss *= strategy_multiplier
        
        return min(stop_loss, 0.1)  # Max 10% stop loss
    
    def _calculate_take_profit(self, volatility: float, strategy_type: str) -> float:
        """Calculate take profit percentage."""
        # Target risk-reward ratio of at least 2:1
        stop_loss = self._calculate_stop_loss(volatility, strategy_type)
        take_profit = stop_loss * 2.5
        
        return min(take_profit, 0.25)  # Max 25% take profit
    
    def _approve_trade(self, position_size: float, risk_level: str) -> bool:
        """Approve or reject trade based on risk parameters."""
        # Don't trade if position size is too small
        if position_size < 0.001:
            logger.warning("Trade rejected: Position size too small")
            return False
        
        # Don't trade under extreme risk
        if risk_level == RiskLevel.EXTREME and self.total_exposure > 0.5:
            logger.warning("Trade rejected: Extreme risk with high exposure")
            return False
        
        # Don't exceed total exposure limit
        if self.total_exposure + position_size > 0.8:
            logger.warning("Trade rejected: Would exceed exposure limit")
            return False
        
        return True
    
    def update_portfolio(self, portfolio_value: float):
        """Update current portfolio value."""
        self.portfolio_value = portfolio_value
        logger.info(f"Portfolio value updated: ${portfolio_value:,.2f}")
    
    def open_position(self, position_id: str, position_data: Dict[str, Any]):
        """Register a new open position."""
        self.active_positions[position_id] = position_data
        self.total_exposure += position_data.get('size', 0)
        logger.info(f"Position opened: {position_id}")
    
    def close_position(self, position_id: str):
        """Close and remove a position."""
        if position_id in self.active_positions:
            position = self.active_positions.pop(position_id)
            self.total_exposure -= position.get('size', 0)
            logger.info(f"Position closed: {position_id}")
    
    def get_portfolio_status(self) -> Dict[str, Any]:
        """Get current portfolio risk status."""
        return {
            'portfolio_value': self.portfolio_value,
            'total_exposure': self.total_exposure,
            'available_capacity': 1.0 - self.total_exposure,
            'active_positions': len(self.active_positions),
            'max_risk_per_trade': self.max_portfolio_risk,
            'max_position_size': self.max_position_size
        }
