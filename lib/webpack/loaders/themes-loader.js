const fs = require('fs');
const path = require('path');
const LOADER_NAME = 'themes-loader';
const schemaUtils = require('schema-utils');
const usePattern = /@use\s+['"](.+?)['"];/g;

const schema = {
    type: 'object',
    properties: {
        silent: {
            type: 'boolean',
            default: 'false',
        },
    },
};

/**
 * Takes the original entrypoint's SCSS source code, and replaces `@use` paths
 * to point to default partial files in `/default` folder of the module, if corresponding
 * partial file does not exist in the theme folder. This way, it is no longer necessary to 
 * copy over files from `default` into `<THEME NAME>` folder, manually modify `@use` paths.
 * 
 * Source code of the default entrypoint is returned unmodified.
 * 
 * @param {String} source Source code of the entrypoint file.
 * @returns Source code with modified `@use` paths.
 */
function themesLoader(source) {
    const options = this.getOptions();

    schemaUtils.validate(schema, options, {
        name: 'Themes loader',
        baseDataPath: 'options',
    });

    const logger = this.getLogger(LOADER_NAME);

    if (this.context.endsWith('default')) {
        return source;
    }

    return source.replace(usePattern, (match, atUsePath) => {
        if (atUsePath.startsWith('~')) {
            return match;
        }

        if (!atUsePath.endsWith('.scss')) {
            atUsePath += '.scss';
        }

        const expectedPath = path.join(this.context, atUsePath);
        const defaultDirectory = path.join(path.dirname(this.context), 'default');

        if (fs.existsSync(expectedPath)) {
            !options.silent && logger.info(`Partial "${expectedPath}" already exists, skipping...`);
            return match;
        }

        const newPath = `${path.relative(path.join(this.context), path.join(defaultDirectory, atUsePath))}`;
        const replacedAtUse = `@use '${newPath}';`;
        !options.silent && logger.info(`[theme: ${path.basename(this.context)}, at: ${this.context}] Resolved into: ${replacedAtUse}`);

        return replacedAtUse;
    });
}

module.exports = themesLoader;
