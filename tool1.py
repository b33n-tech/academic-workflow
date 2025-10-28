import React, { useState, useEffect } from 'react';
import { ChevronUp, ChevronDown, Trash2, Plus, Download, Upload, Copy } from 'lucide-react';

const LEVELS = [
  'Titre 1: I.',
  'Titre 2: I.1.',
  'Titre 3: I.1.a.',
  'Titre 4: I.1.a.1.',
  'Titre 5: I.1.a.1.a'
];

const STORAGE_KEY = 'memo_architecture_v1';

function generateId() {
  return Date.now() + Math.random().toString(36).substr(2, 9);
}

export default function MemoArchitecture() {
  const [blocks, setBlocks] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });
  const [selectedId, setSelectedId] = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(blocks));
  }, [blocks]);

  const pushHistory = () => {
    setHistory(h => [...h.slice(-39), JSON.parse(JSON.stringify(blocks))]);
  };

  const undo = () => {
    if (history.length === 0) return;
    const last = history[history.length - 1];
    setBlocks(last);
    setHistory(h => h.slice(0, -1));
  };

  const addBlock = () => {
    pushHistory();
    setBlocks([...blocks, {
      id: generateId(),
      title: '',
      level: 'Titre 2: I.1.',
      pitch: '',
      summary: '',
      comments: []
    }]);
  };

  const removeBlock = (id) => {
    pushHistory();
    setBlocks(blocks.filter(b => b.id !== id));
    if (selectedId === id) setSelectedId(null);
  };

  const updateBlock = (id, field, value) => {
    setBlocks(blocks.map(b => b.id === id ? { ...b, [field]: value } : b));
  };

  const moveBlock = (id, direction) => {
    pushHistory();
    const idx = blocks.findIndex(b => b.id === id);
    if (idx === -1) return;
    const newIdx = direction === 'up' ? idx - 1 : idx + 1;
    if (newIdx < 0 || newIdx >= blocks.length) return;
    const newBlocks = [...blocks];
    [newBlocks[idx], newBlocks[newIdx]] = [newBlocks[newIdx], newBlocks[idx]];
    setBlocks(newBlocks);
  };

  const addComment = (id, text) => {
    if (!text.trim()) return;
    pushHistory();
    updateBlock(id, 'comments', [...(blocks.find(b => b.id === id)?.comments || []), { text, date: new Date().toISOString() }]);
  };

  const exportJSON = () => {
    const dataStr = JSON.stringify(blocks, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'architecture.json';
    a.click();
  };

  const importJSON = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      try {
        const data = JSON.parse(ev.target.result);
        pushHistory();
        setBlocks(data);
      } catch (err) {
        alert('Fichier JSON invalide');
      }
    };
    reader.readAsText(file);
  };

  const copyTitles = () => {
    const titles = blocks.map(b => b.title).filter(t => t).join('\n');
    navigator.clipboard.writeText(titles);
    alert('Titres copiés dans le presse-papier !');
  };

  const selected = blocks.find(b => b.id === selectedId);

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between gap-4 mb-4">
            <h1 className="text-2xl font-bold text-gray-900">🧩 Architecture du Mémoire</h1>
            <div className="flex gap-2">
              <button onClick={addBlock} className="px-4 py-2 bg-indigo-600 text-white rounded-lg flex items-center gap-2 hover:bg-indigo-700">
                <Plus size={16} /> Ajouter
              </button>
              <button onClick={undo} disabled={history.length === 0} className="px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300 disabled:opacity-50">
                ↩️ Undo
              </button>
            </div>
          </div>
          <div className="flex gap-2">
            <button onClick={exportJSON} className="px-3 py-1.5 bg-green-600 text-white text-sm rounded flex items-center gap-2 hover:bg-green-700">
              <Download size={14} /> JSON
            </button>
            <label className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded flex items-center gap-2 cursor-pointer hover:bg-blue-700">
              <Upload size={14} /> Charger
              <input type="file" accept=".json" onChange={importJSON} className="hidden" />
            </label>
            <button onClick={copyTitles} className="px-3 py-1.5 bg-purple-600 text-white text-sm rounded flex items-center gap-2 hover:bg-purple-700">
              <Copy size={14} /> Copier titres
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-4 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <section className="lg:col-span-2 space-y-3">
          {blocks.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              Clique sur "Ajouter" pour créer ton premier bloc
            </div>
          )}
          {blocks.map((block, idx) => (
            <div key={block.id} className={`bg-white rounded-lg shadow-sm border-2 transition ${selectedId === block.id ? 'border-indigo-500' : 'border-gray-200'}`}>
              <div className="p-4">
                <div className="flex items-start justify-between gap-3 mb-3">
                  <div className="flex-1">
                    <input
                      type="text"
                      value={block.title}
                      onChange={(e) => updateBlock(block.id, 'title', e.target.value)}
                      placeholder="Titre du bloc..."
                      className="w-full text-lg font-semibold border-b-2 border-transparent focus:border-indigo-500 outline-none"
                    />
                    <select
                      value={block.level}
                      onChange={(e) => updateBlock(block.id, 'level', e.target.value)}
                      className="mt-2 text-sm text-gray-600 bg-gray-50 rounded px-2 py-1"
                    >
                      {LEVELS.map(l => <option key={l} value={l}>{l}</option>)}
                    </select>
                  </div>
                  <div className="flex gap-1">
                    <button onClick={() => moveBlock(block.id, 'up')} disabled={idx === 0} className="p-1.5 hover:bg-gray-100 rounded disabled:opacity-30">
                      <ChevronUp size={18} />
                    </button>
                    <button onClick={() => moveBlock(block.id, 'down')} disabled={idx === blocks.length - 1} className="p-1.5 hover:bg-gray-100 rounded disabled:opacity-30">
                      <ChevronDown size={18} />
                    </button>
                    <button onClick={() => setSelectedId(block.id)} className={`px-3 py-1 text-sm rounded ${selectedId === block.id ? 'bg-indigo-600 text-white' : 'bg-gray-100 hover:bg-gray-200'}`}>
                      ✏️
                    </button>
                    <button onClick={() => removeBlock(block.id)} className="p-1.5 hover:bg-red-100 text-red-600 rounded">
                      <Trash2 size={18} />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </section>

        <aside className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-sm border p-4 sticky top-4">
            <h2 className="text-lg font-bold mb-4">🧭 Éditeur</h2>
            {!selected ? (
              <p className="text-sm text-gray-500">Sélectionne un bloc pour l'éditer</p>
            ) : (
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium mb-1">Pitch / Sujet</label>
                  <input
                    type="text"
                    value={selected.pitch}
                    onChange={(e) => updateBlock(selected.id, 'pitch', e.target.value)}
                    className="w-full px-3 py-2 border rounded-lg text-sm"
                    placeholder="Sujet rapide..."
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Résumé</label>
                  <textarea
                    value={selected.summary}
                    onChange={(e) => updateBlock(selected.id, 'summary', e.target.value)}
                    className="w-full px-3 py-2 border rounded-lg text-sm"
                    rows={4}
                    placeholder="Résumé détaillé..."
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Commentaires</label>
                  {selected.comments?.map((c, i) => (
                    <div key={i} className="text-xs bg-gray-50 p-2 rounded mb-1">• {c.text}</div>
                  ))}
                  <div className="flex gap-2 mt-2">
                    <input
                      type="text"
                      id={`comment-${selected.id}`}
                      className="flex-1 px-2 py-1 border rounded text-sm"
                      placeholder="Nouveau commentaire..."
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          addComment(selected.id, e.target.value);
                          e.target.value = '';
                        }
                      }}
                    />
                    <button
                      onClick={() => {
                        const input = document.getElementById(`comment-${selected.id}`);
                        addComment(selected.id, input.value);
                        input.value = '';
                      }}
                      className="px-3 py-1 bg-indigo-600 text-white text-sm rounded hover:bg-indigo-700"
                    >
                      ➕
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </aside>
      </main>
    </div>
  );
}
