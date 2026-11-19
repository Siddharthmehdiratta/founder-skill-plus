"use client";
import { Dialog } from "radix-ui";
import { XIcon } from "lucide-react";

/* A pop-up: dims the page, traps focus, closes with Escape or the X. */
export function Modal({ trigger, title, children, wide = false }: { trigger: React.ReactNode; title: string; children: React.ReactNode; wide?: boolean }) {
  return (
    <Dialog.Root>
      <Dialog.Trigger asChild>{trigger}</Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-50 bg-[#081C21]/50 backdrop-blur-sm data-[state=open]:animate-in data-[state=open]:fade-in-0" />
        <Dialog.Content className={`fixed top-1/2 left-1/2 z-50 max-h-[88vh] w-[calc(100vw-2rem)] -translate-x-1/2 -translate-y-1/2 overflow-y-auto rounded-3xl border bg-background p-6 shadow-2xl sm:p-8 data-[state=open]:animate-in data-[state=open]:fade-in-0 data-[state=open]:zoom-in-95 ${wide ? "max-w-2xl" : "max-w-lg"}`}>
          <div className="flex items-start justify-between gap-4">
            <Dialog.Title className="text-xl font-semibold tracking-tight">{title}</Dialog.Title>
            <Dialog.Close className="grid size-9 shrink-0 place-items-center rounded-xl border hover:bg-muted" aria-label="Close"><XIcon className="size-4" /></Dialog.Close>
          </div>
          <Dialog.Description asChild><div className="mt-4 text-[0.97rem] leading-relaxed text-muted-foreground">{children}</div></Dialog.Description>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
