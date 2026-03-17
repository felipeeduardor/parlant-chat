import React from 'react';
import ParlantChat from './embedded-chat-component';

// Exemplo 1: Chat inline em uma página
const ChatPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-center mb-8 text-gray-800">
          🤖 Assistente Dr. CLT
        </h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Informações */}
          <div className="lg:col-span-1 bg-white rounded-2xl p-6 shadow-lg">
            <h2 className="text-xl font-semibold mb-4 text-gray-700">
              Sobre o Assistente
            </h2>
            <div className="space-y-4 text-gray-600">
              <p>
                O Dr. CLT é um assistente especializado em direito trabalhista 
                brasileiro, powered by Parlant.
              </p>
              <div>
                <h3 className="font-medium mb-2">Funcionalidades:</h3>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  <li>Consultas sobre CLT</li>
                  <li>Cálculos trabalhistas</li>
                  <li>Orientações jurídicas</li>
                  <li>Histórico de conversas</li>
                </ul>
              </div>
            </div>
          </div>
          
          {/* Chat */}
          <div className="lg:col-span-2">
            <ParlantChat 
              baseUrl="http://localhost:8800"
              height="600px"
              className="w-full"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

// Exemplo 2: Chat flutuante em qualquer página
const MainApp: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Conteúdo principal da sua aplicação */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-2xl font-bold text-gray-900">
            Minha Aplicação
          </h1>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow p-8">
          <h2 className="text-xl font-semibold mb-4">
            Bem-vindo à nossa plataforma
          </h2>
          <p className="text-gray-600 mb-6">
            Esta é uma aplicação de exemplo que demonstra como integrar 
            o chat do Parlant de forma flutuante. O chat aparece no 
            canto inferior direito e pode ser usado em qualquer página.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((item) => (
              <div key={item} className="bg-gray-50 rounded-lg p-6">
                <h3 className="font-medium mb-2">Card {item}</h3>
                <p className="text-gray-600 text-sm">
                  Conteúdo de exemplo para demonstrar como o chat 
                  flutuante funciona junto com o conteúdo da página.
                </p>
              </div>
            ))}
          </div>
        </div>
      </main>
      
      {/* Chat flutuante - aparece em todas as páginas */}
      <ParlantChat 
        baseUrl="http://localhost:8800"
        floating={true}
      />
    </div>
  );
};

// Exemplo 3: Hook personalizado para gerenciar o chat
const useParlantChat = (baseUrl: string = 'http://localhost:8800') => {
  const [isConnected, setIsConnected] = React.useState(false);
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    const checkConnection = async () => {
      try {
        const response = await fetch(`${baseUrl}/health`);
        setIsConnected(response.ok);
      } catch {
        setIsConnected(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkConnection();
    
    // Verificar conexão a cada 30 segundos
    const interval = setInterval(checkConnection, 30000);
    return () => clearInterval(interval);
  }, [baseUrl]);

  return { isConnected, isLoading };
};

// Exemplo 4: Chat com status personalizado
const ChatWithStatus: React.FC = () => {
  const { isConnected, isLoading } = useParlantChat();

  return (
    <div className="max-w-4xl mx-auto p-8">
      <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
        {/* Header com status */}
        <div className="bg-gradient-to-r from-green-600 to-green-700 p-4">
          <div className="flex items-center justify-between">
            <h2 className="text-white text-lg font-semibold">
              🤖 Assistente Parlant
            </h2>
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${
                isLoading ? 'bg-yellow-400' : 
                isConnected ? 'bg-green-400' : 'bg-red-400'
              }`} />
              <span className="text-white text-sm">
                {isLoading ? 'Conectando...' : 
                 isConnected ? 'Online' : 'Offline'}
              </span>
            </div>
          </div>
        </div>
        
        {/* Chat */}
        <div className="h-96">
          <ParlantChat 
            baseUrl="http://localhost:8800"
            height="100%"
          />
        </div>
      </div>
    </div>
  );
};

export { ChatPage, MainApp, ChatWithStatus, useParlantChat };
