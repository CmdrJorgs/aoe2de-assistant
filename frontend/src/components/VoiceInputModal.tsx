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

export const VoiceInputModal: React.FC<VoiceInputModalProps> = ({ isOpen, onClose }) => {
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
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-lg overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-800 bg-slate-950/60">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center border border-amber-500/30">
              <Mic className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-100">Speech & Voice Snapshot Input</h3>
              <p className="text-xs text-slate-400">Speak RTS match updates in under 5 seconds</p>
            </div>
          </div>
          <button
            onClick={() => {
              handleStopListening();
              onClose();
            }}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-5 space-y-4">
          {/* Microphone Activation Banner */}
          <div className="flex flex-col items-center justify-center py-6 px-4 rounded-xl bg-slate-950 border border-slate-800 text-center relative overflow-hidden">
            {isListening && (
              <div className="absolute inset-0 bg-amber-500/5 animate-pulse flex items-center justify-center pointer-events-none">
                <div className="w-40 h-40 rounded-full border border-amber-500/20 animate-ping" />
              </div>
            )}

            <button
              type="button"
              onClick={isListening ? handleStopListening : handleStartListening}
              className={`relative z-10 w-16 h-16 rounded-full flex items-center justify-center transition-all shadow-xl ${
                isListening
                  ? "bg-rose-600 hover:bg-rose-500 text-white animate-pulse crimson-glow"
                  : "bg-amber-500 hover:bg-amber-400 text-slate-950 gold-glow font-bold"
              }`}
            >
              {isListening ? <MicOff className="w-7 h-7" /> : <Mic className="w-7 h-7" />}
            </button>

            <span className="mt-3 text-xs font-semibold text-slate-200">
              {isListening ? "Listening... Speak your match update" : "Tap to Speak (or paste text below)"}
            </span>
            <span className="text-[11px] text-slate-400 mt-0.5">
              {isListening ? "Example: 'I see 5 Berserks, floating 750 wood'" : "Supports natural AoE2 civs, numbers, units, resources"}
            </span>

            {speechError && (
              <div className="mt-3 flex items-center gap-1.5 text-xs text-rose-400 bg-rose-950/40 border border-rose-900/60 px-3 py-1 rounded-lg">
                <AlertCircle className="w-3.5 h-3.5" />
                <span>{speechError}</span>
              </div>
            )}
          </div>

          {/* Transcript Textarea */}
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1.5 flex items-center justify-between">
              <span>Speech Transcript / Text:</span>
              {voiceConfidence > 0 && (
                <span className="text-[11px] font-mono text-emerald-400">
                  Confidence: {Math.round(voiceConfidence * 100)}%
                </span>
              )}
            </label>
            <textarea
              rows={3}
              value={inputTranscript}
              onChange={(e) => setInputTranscript(e.target.value)}
              placeholder="e.g., 'I'm Franks vs Vikings at 20 min, I have 800 wood and 300 food, enemy has 5 Berserkers and a Castle'"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-amber-500 font-sans"
            />
          </div>

          {/* Preset Example Quick Buttons */}
          <div>
            <span className="text-[11px] font-medium text-slate-400 block mb-1.5">
              Or Try a Quick Example:
            </span>
            <div className="space-y-1.5">
              {VOICE_EXAMPLES.map((ex, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => setInputTranscript(ex)}
                  className="w-full text-left text-[11px] text-slate-300 bg-slate-950 hover:bg-slate-800/80 border border-slate-800/80 hover:border-slate-700 p-2 rounded-lg transition-colors truncate block"
                >
                  💬 &ldquo;{ex}&rdquo;
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-2 px-5 py-3 border-t border-slate-800 bg-slate-950/60">
          <button
            type="button"
            onClick={() => {
              handleStopListening();
              onClose();
            }}
            className="px-4 py-2 rounded-lg text-xs font-semibold text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleApply}
            disabled={!inputTranscript.trim() || isLoading}
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 shadow-md shadow-amber-500/20 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
          >
            <Sparkles className="w-4 h-4" />
            <span>{isLoading ? "Parsing..." : "Apply Snapshot to Wizard"}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
