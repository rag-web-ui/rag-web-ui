import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen bg-black text-white">
      <div className="max-w-7xl mx-auto px-4 py-24">
        {/* Hero Section */}
        <div className="text-center space-y-8 mb-24">
          <h1 className="text-6xl sm:text-7xl font-bold tracking-tight">
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400">
              RAG Web UI
            </span>
          </h1>
          <p className="text-2xl sm:text-3xl text-gray-200 max-w-3xl mx-auto font-light leading-relaxed">
            Experience the next generation of AI interaction.
            <br />
            Powerful. Intuitive. Revolutionary.
          </p>
          <div className="flex flex-col sm:flex-row gap-6 justify-center items-center mt-12">
            <Link
              href="/register"
              className="group relative px-8 py-4 bg-white text-black rounded-full text-lg font-medium transition-all duration-300 hover:bg-opacity-90 w-full sm:w-auto"
            >
              Get Started
              <span className="absolute right-8 top-1/2 transform -translate-y-1/2 transition-transform duration-300 group-hover:translate-x-2">
                →
              </span>
            </Link>
            <Link
              href="/login"
              className="px-8 py-4 bg-white/10 backdrop-blur hover:bg-white/20 rounded-full text-lg font-medium transition-all duration-300 w-full sm:w-auto"
            >
              Sign In
            </Link>
            <a
              href="https://github.com/JohannLai/rag-web-ui"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-8 py-4 bg-white/10 backdrop-blur hover:bg-white/20 rounded-full text-lg font-medium transition-all duration-300 w-full sm:w-auto"
            >
              <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
              </svg>
              GitHub
            </a>
          </div>
          <div className="mt-12 flex justify-center space-x-4">
            <a
              href="https://github.com/JohannLai/rag-web-ui"
              target="_blank"
              rel="noopener noreferrer"
            >
              <img
                alt="GitHub stars"
                src="https://img.shields.io/github/stars/JohannLai/rag-web-ui?style=social"
                className="h-6"
              />
            </a>
            <img
              alt="License"
              src="https://img.shields.io/github/license/JohannLai/rag-web-ui"
              className="h-6"
            />
            <img
              alt="Python version"
              src="https://img.shields.io/badge/python-3.9+-blue.svg"
              className="h-6"
            />
            <img
              alt="Node version"
              src="https://img.shields.io/badge/node-%3E%3D18-green.svg"
              className="h-6"
            />
          </div>
        </div>

        {/* Features Section */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
          <div className="group relative">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-3xl opacity-0 group-hover:opacity-10 transition-opacity duration-300" />
            <div className="relative p-8 rounded-3xl bg-white/5 backdrop-blur-lg border border-white/10 transition-transform duration-300 group-hover:-translate-y-2">
              <div className="h-16 w-16 rounded-full bg-gradient-to-r from-blue-400 to-blue-600 flex items-center justify-center mb-6">
                <svg
                  className="h-8 w-8 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 10V3L4 14h7v7l9-11h-7z"
                  />
                </svg>
              </div>
              <h3 className="text-2xl font-semibold text-white mb-4">
                Powerful RAG Engine
              </h3>
              <p className="text-gray-400 leading-relaxed">
                Harness the power of state-of-the-art AI models with our
                advanced retrieval and generation system. Built for performance
                and scalability.
              </p>
            </div>
          </div>

          <div className="group relative">
            <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-3xl opacity-0 group-hover:opacity-10 transition-opacity duration-300" />
            <div className="relative p-8 rounded-3xl bg-white/5 backdrop-blur-lg border border-white/10 transition-transform duration-300 group-hover:-translate-y-2">
              <div className="h-16 w-16 rounded-full bg-gradient-to-r from-purple-400 to-purple-600 flex items-center justify-center mb-6">
                <svg
                  className="h-8 w-8 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"
                  />
                </svg>
              </div>
              <h3 className="text-2xl font-semibold text-white mb-4">
                Seamless Integration
              </h3>
              <p className="text-gray-400 leading-relaxed">
                Effortlessly connect with your existing tech stack. Our flexible
                API and comprehensive SDK make integration a breeze.
              </p>
            </div>
          </div>

          <div className="group relative">
            <div className="absolute inset-0 bg-gradient-to-r from-pink-500 to-red-500 rounded-3xl opacity-0 group-hover:opacity-10 transition-opacity duration-300" />
            <div className="relative p-8 rounded-3xl bg-white/5 backdrop-blur-lg border border-white/10 transition-transform duration-300 group-hover:-translate-y-2">
              <div className="h-16 w-16 rounded-full bg-gradient-to-r from-pink-400 to-pink-600 flex items-center justify-center mb-6">
                <svg
                  className="h-8 w-8 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                  />
                </svg>
              </div>
              <h3 className="text-2xl font-semibold text-white mb-4">
                Real-time Analytics
              </h3>
              <p className="text-gray-400 leading-relaxed">
                Gain deep insights into your RAG system's performance with our
                comprehensive analytics dashboard and monitoring tools.
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
