"use client";

export function InsightCard({ text }: { text: string }) {
  // Split by ** for bold handling, and by \n for paragraphs
  const paragraphs = text.split("\n").filter((p) => p.trim());

  return (
    <div className="rounded-xl bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-100 p-6 mb-6">
      <div className="flex items-start gap-3">
        <span className="text-2xl mt-0.5">💡</span>
        <div className="space-y-2 text-sm text-gray-700 leading-relaxed">
          {paragraphs.map((p, i) => (
            <p key={i} dangerouslySetInnerHTML={{ __html: formatBold(p) }} />
          ))}
        </div>
      </div>
    </div>
  );
}

function formatBold(text: string): string {
  return text.replace(/\*\*(.+?)\*\*/g, '<strong class="text-gray-900">$1</strong>');
}
