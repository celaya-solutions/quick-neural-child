#!/bin/bash
# Syncs messages between twins. Run periodically or before each day.
cp "/Users/christophercelaya/Desktop/neural-child/messages/outgoing/"* "/Users/christophercelaya/Desktop/neural-child-twin/messages/incoming/" 2>/dev/null || true
cp "/Users/christophercelaya/Desktop/neural-child-twin/messages/outgoing/"* "/Users/christophercelaya/Desktop/neural-child/messages/incoming/" 2>/dev/null || true
