import React, { useState } from 'react';
import { Search, Loader2, Bot, User } from 'lucide-react';

function App() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userMsg = { role: 'user', content: query };
    setMessages(prev => [...prev, userMsg]);
    setQuery('');
    setIsLoading(true);

    try {
        const response = await fetch('http://localhost:8000/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: userMsg.content })
        });
        const data = await response.json();
        
        setMessages(prev => [...prev, { role: 'agent', content: data.answer }]);
    } catch (error) {
        setMessages(prev => [...prev, { role: 'agent', content: 'Error connecting to the agent.' }]);
    } finally {
        setIsLoading(false);
    }
  };

  // Helper to safely render text with basic line breaks
  const renderContent = (text) => {
      return text.split('\n').map((line, i) => (
          <span key={i}>{line}<br/></span>
      ));
  };

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 font-sans flex flex-col items-center py-10 px-4">
      <div className="w-full max-w-3xl flex-grow flex flex-col gap-6 mb-24">
        <h1 className="text-3xl font-bold text-center text-blue-400 mb-8">Ask-the-Web Agent</h1>
        
        {messages.map((msg, index) => (
          <div key={index} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {msg.role === 'agent' && <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center shrink-0"><Bot size={18}/></div>}
            
            <div className={`p-4 rounded-2xl max-w-[85%] ${msg.role === 'user' ? 'bg-gray-800 border border-gray-700' : 'bg-transparent'}`}>
              <div className="prose prose-invert max-w-none text-sm md:text-base leading-relaxed">
                  {renderContent(msg.content)}
              </div>
            </div>

            {msg.role === 'user' && <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center shrink-0"><User size={18}/></div>}
          </div>
        ))}
        {isLoading && (
            <div className="flex gap-4 items-center text-gray-400">
                <Loader2 className="animate-spin" size={20} />
                <span className="text-sm">Agent is thinking and searching the web...</span>
            </div>
        )}
      </div>

      <div className="fixed bottom-0 w-full max-w-3xl p-4 bg-gray-900 border-t border-gray-800">
        <form onSubmit={handleSubmit} className="relative flex items-center">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask anything..."
            className="w-full bg-gray-800 border border-gray-700 rounded-full py-4 pl-6 pr-14 focus:outline-none focus:border-blue-500 transition-colors"
          />
          <button 
            type="submit" 
            disabled={isLoading}
            className="absolute right-2 p-2 bg-blue-600 rounded-full hover:bg-blue-500 disabled:opacity-50 transition-colors"
          >
            <Search size={20} />
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;
