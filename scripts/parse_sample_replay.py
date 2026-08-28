"""
AoE2 Replay Parser Prototype
Demonstrates extracting metadata, player states, and operations from .aoe2record files.
"""

import os
import sys
import json
from aoe2rec_py import RecSummary
from aoe2rec_py.aoe2rec_py import parse_rec

SAMPLE_PATH = "/home/djorgs/Downloads/SD-AgeIIDE_Replay_502556700.aoe2record"

def parse_replay_sample(filepath: str):
    if not os.path.exists(filepath):
        print(f"Error: File not found at {filepath}")
        return

    print(f"[*] Parsing AoE2 recorded game: {filepath}")
    
    # 1. Summary Metadata
    with open(filepath, "rb") as f:
        summary = RecSummary(f)
        players = summary.get_players()
        duration = summary.get_duration()
        diplomacy = summary.get_diplomacy()

    print("\n--- Match Summary ---")
    print(f"Duration: {duration}")
    print(f"Diplomacy: {diplomacy}")
    print("\nPlayers:")
    for idx, p in enumerate(players):
        print(f"  Player {p.get('number')} ({p.get('name')}): Civ ID {p.get('civilization')}, ELO {p.get('rate_snapshot')}, Winner: {p.get('winner')}, eAPM: {p.get('eapm')}")

    # 2. Deep Binary Operations & State Stream
    with open(filepath, "rb") as f:
        raw_bytes = f.read()
        parsed = parse_rec(raw_bytes)
        
    operations = parsed.get("operations", [])
    print(f"\nTotal Operations Parsed: {len(operations):,}")
    
    # Sample chat & first operations
    chats = [op for op in operations if "Chat" in op]
    print(f"Chat messages found: {len(chats)}")
    for chat in chats[:5]:
        print("  Chat:", chat["Chat"].get("text"))

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else SAMPLE_PATH
    parse_replay_sample(target)
