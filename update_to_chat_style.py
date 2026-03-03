#!/usr/bin/env python3
"""
Convert agents from rigid analyzing/alert messages to freeform chat
"""

import re

# Mapping of old analyzing messages to conversational chat
chat_templates = {
    'analyzing_start': [
        "Looking at {count} {category} markets... 👀",
        "Diving into {count} {category} markets",
        "Starting analysis on {count} {category} opportunities",
        "Scanning {count} {category} markets for edge",
        "Let me check out these {count} {category} markets..."
    ],
    'market_analyzing': [
        "Interesting... checking out: {question}",
        "Hmm, {question} - let me run the numbers",
        "Analyzing: {question}",
        "{question} caught my attention",
        "Running analysis on: {question}"
    ],
    'rejection_edge': [
        "❌ {question} - edge only {edge:.1%}, need {min_edge:.1%}+",
        "Passing on {question} - edge too thin ({edge:.1%})",
        "Not enough edge here: {question} ({edge:.1%} vs {min_edge:.1%} min)",
        "{question} - only {edge:.1%} edge, moving on..."
    ],
    'rejection_conviction': [
        "❌ {question} - conviction {conviction:.1%} below my {min_conviction:.1%} threshold",
        "Low conviction on {question} ({conviction:.1%}), passing",
        "Not confident enough: {question} ({conviction:.1%})",
        "{question} - conviction too low ({conviction:.1%})"
    ],
    'thesis_posted': [
        "✅ Posted thesis: {question} | {edge:+.1%} edge, {conviction:.1%} conviction",
        "Thesis up: {question} - {side} @ {current_odds:.1%} → {thesis_odds:.1%}",
        "Strong {side} thesis on: {question} ({edge:+.1%} edge)",
        "Found one! {question} | Edge: {edge:+.1%} | Conv: {conviction:.1%}",
        "Posting {side} thesis: {question} ({conviction:.1%} conviction)"
    ],
    'no_markets': [
        "No {category} markets meet volume threshold today 🤷",
        "Zero {category} markets available right now",
        "Nothing in {category} to analyze today",
        "Quiet day for {category} markets"
    ],
    'complete': [
        "Done! Generated {count} theses",
        "Analysis complete - {count} theses posted",
        "Finished: {count} actionable theses",
        "That's a wrap - {count} opportunities found"
    ]
}

print("Chat templates ready for agent updates")
