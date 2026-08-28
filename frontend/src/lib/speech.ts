/**
 * Web Speech API hook and utility for real-time RTS voice updates.
 */

export interface SpeechHandlerOptions {
  onResult: (transcript: string, isFinal: boolean) => void;
  onError: (error: string) => void;
  onEnd: () => void;
}

interface ISpeechRecognitionEvent {
  resultIndex: number;
  results: {
    length: number;
    [index: number]: {
      isFinal: boolean;
      [index: number]: {
        transcript: string;
      };
    };
  };
}

interface ISpeechRecognitionErrorEvent {
  error: string;
}

interface ISpeechRecognitionInstance {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onresult: ((event: ISpeechRecognitionEvent) => void) | null;
  onerror: ((event: ISpeechRecognitionErrorEvent) => void) | null;
  onend: (() => void) | null;
  start: () => void;
  stop: () => void;
}

export class SpeechRecognitionService {
  private recognition: ISpeechRecognitionInstance | null = null;
  private isRunning: boolean = false;

  constructor() {
    if (typeof window !== "undefined") {
      const windowWithSpeech = window as unknown as {
        SpeechRecognition?: new () => ISpeechRecognitionInstance;
        webkitSpeechRecognition?: new () => ISpeechRecognitionInstance;
      };
      const SpeechRecognitionConstructor =
        windowWithSpeech.SpeechRecognition || windowWithSpeech.webkitSpeechRecognition;
      if (SpeechRecognitionConstructor) {
        this.recognition = new SpeechRecognitionConstructor();
        this.recognition.continuous = true;
        this.recognition.interimResults = true;
        this.recognition.lang = "en-US";
      }
    }
  }

  public isSupported(): boolean {
    return this.recognition !== null;
  }

  public start(options: SpeechHandlerOptions): boolean {
    if (!this.recognition || this.isRunning) return false;

    this.recognition.onresult = (event: ISpeechRecognitionEvent) => {
      let interimTranscript = "";
      let finalTranscript = "";

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        } else {
          interimTranscript += event.results[i][0].transcript;
        }
      }

      const text = finalTranscript || interimTranscript;
      options.onResult(text, Boolean(finalTranscript));
    };

    this.recognition.onerror = (event: ISpeechRecognitionErrorEvent) => {
      console.warn("Speech recognition event error:", event.error);
      options.onError(event.error || "Speech recognition error");
    };

    this.recognition.onend = () => {
      this.isRunning = false;
      options.onEnd();
    };

    try {
      this.recognition.start();
      this.isRunning = true;
      return true;
    } catch (e) {
      console.error("Failed to start speech recognition:", e);
      return false;
    }
  }

  public stop(): void {
    if (this.recognition && this.isRunning) {
      this.recognition.stop();
      this.isRunning = false;
    }
  }
}

export const speechService = new SpeechRecognitionService();
