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
