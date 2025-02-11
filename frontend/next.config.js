/** @type {import('next').NextConfig} */
module.exports = {
  output: "standalone",
  experimental: {
    // This is needed for standalone output to work correctly
    outputFileTracingRoot: undefined,
    outputStandalone: true,
    skipMiddlewareUrlNormalize: true,
    skipTrailingSlashRedirect: true,
  },
};
