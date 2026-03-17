import React, { useState, useEffect } from 'react';

interface ParlantChatProps {
  baseUrl?: string;
  width?: string;
  height?: string;
  className?: string;
  floating?: boolean;
  theme?: 'light' | 'dark';
}

const ParlantChat: React.FC<ParlantChatProps> = ({
  baseUrl = 'http://localhost:8800',
  width = '100%',
  height = '600px',
  className = '',
  floating = false,
  theme = 'light'
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [serverStatus, setServerStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  useEffect(() => {
    // Verificar se o servidor Parlant está rodando
    const checkServer = async () => {
      try {
        const response = await fetch(`${baseUrl}/health`);
        if (response.ok) {
          setServerStatus('online');
        } else {
          setServerStatus('offline');
        }
      } catch (error) {
        setServerStatus('offline');
      }
    };

    checkServer();
  }, [baseUrl]);

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  if (floating) {
    return (
      <>
        {/* Botão flutuante */}
        <button
          onClick={toggleChat}
          className={`fixed bottom-5 right-5 w-14 h-14 bg-green-600 hover:bg-green-700 
                     text-white rounded-full shadow-lg hover:shadow-xl transition-all 
                     duration-300 flex items-center justify-center text-xl z-50 ${className}`}
          aria-label="Abrir chat"
        >
          {isOpen ? '✕' : '💬'}
        </button>

        {/* Chat flutuante */}
        {isOpen && (
          <div className="fixed bottom-20 right-5 w-96 h-[500px] bg-white rounded-2xl 
                         shadow-2xl z-40 overflow-hidden animate-in slide-in-from-bottom-2">
            <div className="h-full">
              {serverStatus === 'online' ? (
                <iframe
                  src={`${baseUrl}/chat`}
                  width="100%"
                  height="100%"
                  frameBorder="0"
                  title="Parlant Chat"
                  className="rounded-2xl"
                />
              ) : (
                <div className="h-full flex items-center justify-center bg-gray-50 rounded-2xl">
                  <div className="text-center p-6">
                    <div className="text-4xl mb-4">🤖</div>
                    <h3 className="text-lg font-semibold text-gray-700 mb-2">
                      Chat Indisponível
                    </h3>
                    <p className="text-gray-500 text-sm">
                      {serverStatus === 'checking' 
                        ? 'Verificando conexão...' 
                        : 'Servidor Parlant offline'}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </>
    );
  }

  // Chat inline
  return (
    <div className={`${className}`} style={{ width, height }}>
      {serverStatus === 'online' ? (
        <iframe
          src={`${baseUrl}/chat`}
          width="100%"
          height="100%"
          frameBorder="0"
          title="Parlant Chat"
          className="rounded-2xl shadow-lg"
        />
      ) : (
        <div className="h-full flex items-center justify-center bg-gray-50 rounded-2xl shadow-lg">
          <div className="text-center p-8">
            <div className="text-6xl mb-6">🤖</div>
            <h3 className="text-xl font-semibold text-gray-700 mb-3">
              Chat Indisponível
            </h3>
            <p className="text-gray-500">
              {serverStatus === 'checking' 
                ? 'Verificando conexão com o servidor...' 
                : 'Servidor Parlant não está rodando'}
            </p>
            <p className="text-gray-400 text-sm mt-2">
              Certifique-se que o Parlant está rodando em {baseUrl}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ParlantChat;
