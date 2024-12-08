# src/analysis/session_analyzer.py

import matplotlib.pyplot as plt
from pathlib import Path
import logging
from datetime import datetime

class SessionAnalyzer:
    def __init__(self):
        self.winnings_history = []
        self.cumulative_winnings = 0
        self.hands_played = 0
        
    def record_hand(self, hand_winnings):
        """Record the results of a single hand"""
        self.hands_played += 1
        self.cumulative_winnings += hand_winnings
        self.winnings_history.append(self.cumulative_winnings)
        
    def merge_results(self, other_analyzer):
        """Merge results from another analyzer"""
        for winnings in other_analyzer.winnings_history:
            # 相対的な収支を計算して追加
            relative_winnings = winnings - other_analyzer.winnings_history[0] + (self.cumulative_winnings if self.winnings_history else 0)
            self.winnings_history.append(relative_winnings)
            
        self.cumulative_winnings = self.winnings_history[-1] if self.winnings_history else 0
        self.hands_played += other_analyzer.hands_played
    def create_graph(self, save_dir):
        """Create and save the winnings graph"""
        if not self.winnings_history:
            logging.warning("No hand data available for graph creation")
            return None
            
        # Create figure
        plt.figure(figsize=(12, 6))
        
        # Plot main line
        plt.plot(
            range(1, len(self.winnings_history) + 1),
            self.winnings_history,
            label='Cumulative Winnings',
            color='blue',
            linewidth=2
        )
        
        # Add zero line
        plt.axhline(y=0, color='red', linestyle='--', alpha=0.3, label='Break Even')
        
        # Customize graph
        plt.title('Poker Session Results', fontsize=14, pad=15)
        plt.xlabel('Number of Hands', fontsize=12)
        plt.ylabel('Cumulative Winnings (Chips)', fontsize=12)
        
        # Add grid
        plt.grid(True, alpha=0.3)
        
        # Add legend
        plt.legend(fontsize=10)
        
        # Add final stats annotation
        stats_text = f'Final Balance: {self.cumulative_winnings:,} chips\n'
        stats_text += f'Hands Played: {self.hands_played}\n'
        stats_text += f'Average per Hand: {self.cumulative_winnings/self.hands_played:,.1f}'
        
        plt.annotate(
            stats_text,
            xy=(0.02, 0.98),
            xycoords='axes fraction',
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'),
            va='top',
            fontsize=10
        )
        
        # Save the graph
        graph_path = save_dir / 'session_graph.png'
        plt.savefig(graph_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logging.info(f"Graph saved as: {graph_path}")
        return graph_path
        
    def get_statistics(self):
        """Get session statistics"""
        if not self.winnings_history:
            return None
            
        return {
            'hands_played': self.hands_played,
            'final_balance': self.cumulative_winnings,
            'average_per_hand': self.cumulative_winnings / self.hands_played,
            'max_balance': max(self.winnings_history),
            'min_balance': min(self.winnings_history)
        }
