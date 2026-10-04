import { useEffect, useState } from "react";

import { Button } from "./ui";

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed" }>;
}

function isIosDevice(): boolean {
  return (
    /iphone|ipad|ipod/i.test(navigator.userAgent) &&
    !(window as unknown as { MSStream?: unknown }).MSStream
  );
}

function isStandalone(): boolean {
  return (
    window.matchMedia("(display-mode: standalone)").matches ||
    (navigator as unknown as { standalone?: boolean }).standalone === true
  );
}

function ArrowIcon({ className = "h-4 w-4" }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M12 4v12m0 0l-5-5m5 5l5-5M5 20h14" />
    </svg>
  );
}

export function InstallButton({
  className = "",
  iconOnly = false,
}: {
  className?: string;
  iconOnly?: boolean;
}) {
  const [promptEvent, setPromptEvent] =
    useState<BeforeInstallPromptEvent | null>(null);
  const [installed, setInstalled] = useState(isStandalone());
  const [showHelp, setShowHelp] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const onPrompt = (event: Event) => {
      event.preventDefault();
      setPromptEvent(event as BeforeInstallPromptEvent);
    };

    const onInstalled = () => {
      setInstalled(true);
      setPromptEvent(null);
    };

    window.addEventListener("beforeinstallprompt", onPrompt);
    window.addEventListener("appinstalled", onInstalled);

    return () => {
      window.removeEventListener("beforeinstallprompt", onPrompt);
      window.removeEventListener("appinstalled", onInstalled);
    };
  }, []);

  // Already installed — nothing to offer.
  if (installed) {
    return null;
  }

  async function handleTap() {
    // Native install prompt when the browser offers one.
    if (promptEvent) {
      setBusy(true);

      try {
        await promptEvent.prompt();
        await promptEvent.userChoice;
      } finally {
        setPromptEvent(null);
        setBusy(false);
      }

      return;
    }

    // Otherwise show manual install steps.
    setShowHelp((value) => !value);
  }

  const helpText = isIosDevice() ? (
    <p>
      On iPhone: tap <strong>Share</strong> in Safari, then{" "}
      <strong>Add to Home Screen</strong>.
    </p>
  ) : (
    <p>
      Open the browser menu <strong>⋮</strong>, then choose{" "}
      <strong>Install app</strong> / <strong>Add to Home Screen</strong>.
    </p>
  );

  if (iconOnly) {
    return (
      <div className={`relative ${className}`}>
        <button
          type="button"
          onClick={handleTap}
          disabled={busy}
          aria-expanded={showHelp}
          aria-label="Download app to your phone"
          title="Download app to your phone"
          className="flex h-10 w-10 items-center justify-center rounded-xl text-slate-600 transition hover:bg-slate-100 active:scale-95 disabled:opacity-50"
        >
          <ArrowIcon className="h-5 w-5" />
        </button>
        {showHelp && !promptEvent && (
          <div className="absolute right-0 top-full z-50 mt-2 w-56 rounded-xl border border-slate-200 bg-white p-3 text-xs leading-relaxed text-slate-600 shadow-pop">
            {helpText}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className={className}>
      <Button
        type="button"
        variant="secondary"
        onClick={handleTap}
        disabled={busy}
        aria-expanded={showHelp}
        className="w-full"
      >
        <ArrowIcon />
        {busy ? "Installing…" : "Install app"}
      </Button>
      {showHelp && !promptEvent && (
        <div className="mt-2 rounded-xl bg-slate-100 px-3 py-2 text-xs leading-relaxed text-slate-600">
          {helpText}
        </div>
      )}
    </div>
  );
}
