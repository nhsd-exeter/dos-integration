#!/bin/bash

# https://apple.stackexchange.com/questions/264691/is-it-possible-to-automatically-switch-between-scrolling

osascript <<HEREDOC
    on run
        try
            tell application "System Preferences"
                set current pane to pane "com.apple.preference.mouse"
                activate
            end tell
            tell application "System Events" to tell process "System Preferences"
                tell radio button 1 of tab group 1 of window 1 to if value is 0 then click
                set cbValue to value of (click checkbox 1 of tab group 1 of window 1)
            end tell
            tell application "System Preferences" to quit
            tell me
                activate
                if cbValue is equal to 1 then
                    -- display dialog "Natural scrolling is now active." buttons {"OK"} default button 1 with title "Toggle Natural Scrolling" giving up after 3
                    display notification "Natural scrolling is now active."
                else
                    -- display dialog "Natural scrolling is no longer active." buttons {"OK"} default button 1 with title "Toggle Natural Scrolling" giving up after 3
                    display notification "Natural scrolling is no longer active."
                end if
            end tell
        on error eStr number eNum
            activate
            display dialog eStr & " number " & eNum buttons {"OK"} default button 1 with title "Toggle Natural Scrolling" with icon caution
        end try
    end run
HEREDOC
