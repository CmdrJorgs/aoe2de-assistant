"use client";

import React, { useState, useEffect } from "react";
import { useCoachStore } from "@/lib/store";
import { speechService } from "@/lib/speech";
import { Mic, MicOff, Sparkles, X, AlertCircle } from "lucide-react";

interface VoiceInputModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const VOICE_EXAMPLES = [
  "I'm playing Franks vs Vikings at 22 minutes. I have 750 wood, 320 food, and 48 villagers. I spotted 5 Berserkers and a Castle.",
  "Britons vs Mayans, 18 minutes Castle Age. I have 14 on wood, 16 on food, and I spotted 12 archers and 2 ranges.",
  "I have 800 wood and 200 food. Enemy is massing 10 knights and 2 stables. My ELO is 1200.",
];

export const VoiceInputModal: React.FC<VoiceInputModalProps> = ({
  isOpen,
  onClose,
}) => {
  const {
    isListening,
    setIsListening,
    voiceTranscript,
    setVoiceTranscript,
    applyVoiceTranscript,
    voiceConfidence,
    isLoading,
  } = useCoachStore();

  const [inputTranscript, setInputTranscript] = useState<string>("");
  const [speechError, setSpeechError] = useState<string | null>(null);

  useEffect(() => {
    if (voiceTranscript) {
      setInputTranscript(voiceTranscript);
    }
  }, [voiceTranscript]);

  if (!isOpen) return null;

  const handleStartListening = () => {
    setSpeechError(null);
    const started = speechService.start({
      onResult: (text) => {
        setVoiceTranscript(text);
        setInputTranscript(text);
      },
      onError: (err) => {
        setSpeechError(err);
        setIsListening(false);
      },
      onEnd: () => {
        setIsListening(false);
      },
    });

    if (started) {
      setIsListening(true);
    } else {
      setSpeechError("Microphone access could not be started.");
    }
  };

  const handleStopListening = () => {
    speechService.stop();
    setIsListening(false);
  };

  const handleApply = async () => {
    if (!inputTranscript.trim()) return;
    handleStopListening();
    await applyVoiceTranscript(inputTranscript);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-charcoal-ink/80 backdrop-blur-xs animate-in fade-in duration-200">
      <div className="bg-surface-container parchment-panel border border-outline-variant rounded-xl w-full max-w-lg overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-outline-variant bg-parchment-deep">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-full bg-gold-leaf text-on-primary flex items-center justify-center border border-surface-tint">
              <Mic className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-base font-headline-md font-bold text-primary">
                Speech & Voice Tactical Input
              </h3>
              <p className="text-xs font-body-md text-on-surface-variant">
                Speak RTS match updates in under 5 seconds
              </p>
            </div>
          </div>
          <button
            onClick={() => {
              handleStopListening();
              onClose();
            }}
            className="p-1 rounded text-on-surface-variant hover:text-blood-accent hover:bg-surface-variant transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-5 space-y-4">
          {/* Microphone Activation Banner */}
          <div className="flex flex-col items-center justify-center py-6 px-4 rounded-lg bg-surface border border-outline-variant text-center relative overflow-hidden shadow-inner">
            {isListening && (
              <div className="absolute inset-0 bg-gold-leaf/10 animate-pulse flex items-center justify-center pointer-events-none">
                <div className="w-36 h-36 rounded-full border border-gold-leaf/30 animate-ping" />
              </div>
            )}

            <button
              type="button"
              onClick={isListening ? handleStopListening : handleStartListening}
              className={`relative z-10 w-16 h-16 rounded-full flex items-center justify-center transition-all shadow-md cursor-pointer border ${
                isListening
                  ? "bg-blood-accent hover:bg-secondary text-on-primary border-gold-leaf animate-pulse"
                  : "bg-charcoal-ink hover:bg-blood-accent text-on-primary border-gold-leaf"
              }`}
            >
              {isListening ? (
                <MicOff className="w-7 h-7" />
              ) : (
                <Mic className="w-7 h-7 text-gold-leaf" />
              )}
            </button>

            <span className="mt-3 text-sm font-headline-md font-bold text-primary">
              {isListening
                ? "Listening... Speak your match update"
                : "Tap to Speak (or paste text below)"}
            </span>
            <span className="text-xs font-body-md text-on-surface-variant mt-0.5">
              {isListening
                ? "Example: 'I see 5 Berserks, floating 750 wood'"
                : "Supports natural AoE2 civs, numbers, units, and resources"}
            </span>

            {speechError && (
              <div className="mt-3 flex items-center gap-1.5 text-xs text-error bg-error-container border border-error px-3 py-1 rounded">
                <AlertCircle className="w-3.5 h-3.5" />
                <span>{speechError}</span>
              </div>
            )}
          </div>

          {/* Transcript Textarea */}
          <div>
            <label className="block text-xs font-label-tactical text-on-surface mb-1.5 flex items-center justify-between">
              <span>Speech Transcript / Text:</span>
              {voiceConfidence > 0 && (
                <span className="text-[11px] font-label-tactical text-tertiary font-bold">
                  Confidence: {Math.round(voiceConfidence * 100)}%
                </span>
              )}
            </label>
            <textarea
              rows={3}
              value={inputTranscript}
              onChange={(e) => setInputTranscript(e.target.value)}
              placeholder="e.g., 'I'm Franks vs Vikings at 20 min, I have 800 wood and 300 food, enemy has 5 Berserkers and a Castle'"
              className="w-full input-sunken bg-surface-bright rounded-lg p-3 text-xs font-body-md text-on-surface focus:outline-none"
            />
          </div>

          {/* Preset Example Quick Buttons */}
          <div>
            <span className="text-xs font-label-tactical text-on-surface-variant block mb-1.5">
              Or Try a Quick Example:
            </span>
            <div className="space-y-1.5">
              {VOICE_EXAMPLES.map((ex, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => setInputTranscript(ex)}
                  className="w-full text-left text-xs font-body-md text-on-surface-variant bg-surface hover:bg-surface-variant border border-outline-variant p-2 rounded transition-colors truncate block cursor-pointer"
                >
                  💬 &ldquo;{ex}&rdquo;
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-2 px-5 py-3.5 border-t border-outline-variant bg-parchment-deep">
          <button
            type="button"
            onClick={() => {
              handleStopListening();
              onClose();
            }}
            className="px-4 py-2 rounded text-xs font-label-tactical text-on-surface-variant hover:text-blood-accent hover:bg-surface-variant transition-colors cursor-pointer"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleApply}
            disabled={!inputTranscript.trim() || isLoading}
            className="flex items-center gap-1.5 px-4 py-2 rounded text-xs font-label-tactical font-bold bg-charcoal-ink hover:bg-blood-accent text-on-primary border border-gold-leaf shadow-sm disabled:opacity-40 disabled:cursor-not-allowed transition-all cursor-pointer"
          >
            <Sparkles className="w-3.5 h-3.5 text-gold-leaf" />
            <span>{isLoading ? "Parsing..." : "Apply Snapshot to Wizard"}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
