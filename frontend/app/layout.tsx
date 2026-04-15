import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from './providers';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Evolution Dashboard - Sistema Biomimético',
  description: 'Dashboard de monitoramento e controle do sistema evolutivo biomimético',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR" className="dark">
      <body className={`${inter.className} bg-gradient-to-br from-gray-900 to-gray-950 text-gray-100 min-h-screen`}>
        <Providers>
          <div className="container mx-auto px-4 py-8">
            <header className="mb-10">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-500 to-purple-600 bg-clip-text text-transparent">
                    🧬 Evolution Dashboard
                  </h1>
                  <p className="text-gray-400 mt-2">
                    Monitoramento e controle do sistema evolutivo biomimético
                  </p>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="px-4 py-2 bg-gray-800 rounded-lg">
                    <span className="text-sm text-gray-400">API:</span>
                    <span className="ml-2 text-green-400 font-mono">localhost:8000</span>
                  </div>
                </div>
              </div>
            </header>
            <main>{children}</main>
            <footer className="mt-16 pt-8 border-t border-gray-800 text-center text-gray-500 text-sm">
              <p>Sistema Evolutivo Biomimético • Desenvolvido com OpenClaw/Jarvis • {new Date().getFullYear()}</p>
            </footer>
          </div>
        </Providers>
      </body>
    </html>
  );
}