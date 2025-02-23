const { addonBuilder } = require('stremio-addon-sdk');
const axios = require('axios');

const builder = new addonBuilder({
    id: 'org.example.milanaddon',
    version: '1.0.0',
    name: 'Milan Addon',
    description: 'An addon that provides streaming links.',
    catalogs: [],
    resources: ['stream'],
    types: ['movie'],
});

builder.defineStreamHandler(async ({ type, id }) => {
    if (type === 'movie') {
        try {
            const response = await axios.get(`https://https://milan-s-addon.onrender.com/get_m3u8_url?tmdb_id=${id}`);
            const data = response.data;
            if (data.master_url) {
                return {
                    streams: Object.values(data.variants).map(variant => ({
                        title: `VidLink - ${variant.bandwidth} bps`,
                        url: variant.url,
                    })),
                };
            }
        } catch (error) {
            console.error(error);
        }
    }
    return { streams: [] };
});

module.exports = builder.getInterface();
