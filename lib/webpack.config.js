const path = require('path');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const VirtualModulesPlugin = require('webpack-virtual-modules');
const VirtualEntrypointInjectorPlugin = require('./webpack/plugins/virtual-entrypoint-injector-plugin');
const EntryUtils = require('./webpack/utils/entry-utils');

const loadersDir = path.resolve(__dirname, 'webpack', 'loaders');
const isProduction = process.env.NODE_ENV === 'production';
const virtualModulesPlugin = new VirtualModulesPlugin();
const virtualEntrypointInjectorPlugin = new VirtualEntrypointInjectorPlugin(
    virtualModulesPlugin,
    { matchPattern: /\.s[ac]ss$/i }
);

const appPaths = [
    'rarea',
];

const themes = [
    'default',
    'light',
];


const config = {
    entry: {
        'rarea': ['babel-polyfill', '../dev/rarea/js/main.js'],
        'parea': ['babel-polyfill', '../dev/parea/js/main.js'],
        ...EntryUtils.generateCSSEntries({
            themes,
            appPaths,
            silent: false,
        }),
    },
    output: {
        path: path.resolve(__dirname, '../dev/pub'),
        filename: '[name]/build.js',
    },

    watch: true,
    watchOptions: {
      aggregateTimeout: 200,
      poll: 1000,
    },
        
    resolve: {
        modules: [
            "./lib/node_modules",
          ],        
        alias: {
            rarea: path.resolve(__dirname, '../dev/rarea'),
            shared: path.resolve(__dirname, '../dev/shared'),
        },
    },
    plugins: [
        new MiniCssExtractPlugin({ filename: '[name]/build.css' }),

        virtualEntrypointInjectorPlugin,

        virtualModulesPlugin,

        new CopyWebpackPlugin({
            patterns: [
                ...EntryUtils.generateCopyEntries({
                    themes,
                    appPaths,
                    silent: false,
                    rootPath: '../dev',
                    defaultAssets: ['fonts', 'img'],
                }),
            ],
        }),
    ],
    module: {
        rules: [
            {
                test: /\.(js|jsx)$/i,
                loader: 'babel-loader',
            },
            {
                test: /\.s[ac]ss$/i,
                use: [
                    { loader: MiniCssExtractPlugin.loader },
                    { loader: 'css-loader', options: { url: false } },
                    {
                        loader: 'sass-loader',
                        options: {
                            sourceMap: true,
                            sassOptions: {
                                outputStyle: 'compressed',
                            },
                        },
                    },
                    {
                        loader: path.join(loadersDir, 'themes-loader.js'),
                        options: { silent: false },
                    },
                ],
            },
            {
                test: /\.(eot|svg|ttf|woff|woff2|png|jpg|gif)$/i,
                type: 'asset',
            },
        ],
    },
};




module.exports = () => {
    if (isProduction) {
        config.mode = 'production';
    } else {
        config.mode = 'development';
        config.devtool = 'eval-source-map';
    }

    return config;
};
