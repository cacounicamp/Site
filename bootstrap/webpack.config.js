const autoprefixer = require('autoprefixer');
const path = require("path");

module.exports = [{
  entry: ['./app.scss', './app.js'],
  output: {
    path: path.resolve(__dirname, "build"),
    filename: 'bundle.js',
  },
  module: {
    rules: [
      {
        test: /\.scss$/,
        use: [
          {
            loader: 'file-loader',
            options: {
              name: 'bundle.css',
            },
          },
          { loader: 'extract-loader' },
          { loader: 'css-loader' },
          {
            // Para não precisarmos de prefixos
            loader: 'postcss-loader',
            options: {
               plugins: () => [autoprefixer()]
            }
          },
          {
            loader: 'sass-loader',
            options: {
              // Incluímos os pacotes instalados pelo npm
              includePaths: ['./node_modules']
            }
          },
        ],
      },
      {
        test: /\.js$/,
        loader: 'babel-loader',
        query: {
          presets: ['env'],
        },
      }
    ],
  },
  // Configurações tiradas de https://webpack.js.org/configuration/
  target: "web",
  performance: {
    hints: "warning",
    maxAssetSize: 200000, // bytes
    maxEntrypointSize: 400000, // bytes
    assetFilter: function(assetFilename) {
      // Function predicate that provides asset filenames
      return assetFilename.endsWith('.css') || assetFilename.endsWith('.js');
    }
  },
}];
