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

export function InstallButton({ className = "" }: { className?: string }) {
  const [promptEvent, setPromptEvent] =
    useState<BeforeInstallPromptEvent | null>(null);
  const [installed, setInstalled] = useState(isStandalone());
  const [showIosHelp, setShowIosHelp] = useState(false);
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

  if (installed) {
    return null;
  }

  async function handleInstall() {
    if (!promptEvent) {
      return;
    }

    setBusy(true);

    try {
      await promptEvent.prompt();
      await promptEvent.userChoice;
    } finally {
      setPromptEvent(null);
      setBusy(false);
    }
  }

  const icon = (
    <svg
      className="h-4 w-4"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M12 3v12m0 0l-4.5-4.5M12 15l4.5-4.5M4 19h16" />
    </svg>
  );

  // Chrome / Edge / Samsung Internet on an installable build.
  if (promptEvent) {
    return (
      <Button
        type="button"
        variant="secondary"
        onClick={handleInstall}
        disabled={busy}
        className={className}
      >
        {icon}
        {busy ? "Installing…" : "Install app"}
      </Button>
    );
  }

  // iPhone / iPad: no install prompt exists — guide to Share → Add to Home Screen.
  if (isIosDevice()) {
    return (
      <div className={className}>
        <Button
          type="button"
          variant="secondary"
          onClick={() => setShowIosHelp((value) => !value)}
          aria-expanded={showIosHelp}
          className="w-full"
        >
          {icon}
          Install app
        </Button>
        {showIosHelp && (
          <p className="mt-2 rounded-xl bg-slate-100 px-3 py-2 text-xs leading-relaxed text-slate-600">
            On iPhone: tap <strong>Share</strong> in Safari, then{" "}
            <strong>Add to Home Screen</strong>.
          </p>
        )}
      </div>
    );
  }

  return null;
}
