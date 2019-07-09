const path = require('path');

module.exports = {
    entry: './src/app.js',
    mode: 'production',
    target: "web",
    output: {
        filename: 'bundle.js',
        path: path.resolve(__dirname, 'build')
    },
    module: {
        rules: [
            {
                test: /\.(scss)$/,
                use: [
                    {
                        // Adiciona tag <style> de CSS
                        loader: 'style-loader'
                    },
                    {
                        // Para carregar CSS diretamente
                        loader: 'css-loader'
                    },
                    {
                        // Webpack processará CSS também
                        loader: 'postcss-loader',
                        options: {
                            plugins: function () {
                                return [
                                    require('autoprefixer')
                                ];
                            }
                        }
                    },
                    {
                        // Carrega SASS (scss) para CSS
                        loader: 'sass-loader'
                    }
                ]
            }
        ]
    }
};
