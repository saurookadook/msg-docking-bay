import autoprefixer from 'autoprefixer';
import cssnano from 'cssnano';
import postcssImport from 'postcss-import';
import postcssPresetEnv from 'postcss-preset-env';

const isProdBuild = process.env.NODE_ENV === 'production';

export default {
  plugins: [
    postcssImport(),
    postcssPresetEnv({ stage: 2, features: { 'nesting-rules': true } }),
    autoprefixer(),
    ...(isProdBuild ? [cssnano()] : []),
  ],
};
