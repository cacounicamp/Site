const path = require("path");

// Para extrair CSS
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
// Para minimizar output
const TerserJSPlugin = require('terser-webpack-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');

module.exports = {
    entry: "./src/main.js",

    mode: 'production',

    output: {
        filename: "[name].js",
        path: path.join(__dirname, "./build"),
    },

    optimization: {
        minimizer: [new TerserJSPlugin({}), new CssMinimizerPlugin()],
    },

    module: {
        rules: [
            {
                test: /\.(sa|sc|c)ss$/,
                use: [
                    {
                        loader: MiniCssExtractPlugin.loader,
                        options: {
                        },
                    },
                    'css-loader',
                    'sass-loader',
                    'postcss-loader',
                ],
            },
        ],
      
    },

    plugins: [
        new MiniCssExtractPlugin({
            filename: '[name].css',
            ignoreOrder: false
        }),
    ],

};
