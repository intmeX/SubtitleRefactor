import _Kuroshiro from 'kuroshiro';
import KuromojiAnalyzer from 'kuroshiro-analyzer-kuromoji';
import Express from 'express';

const app = Express();
const interopDefault = m => m.default || m;
const Kuroshiro = interopDefault(_Kuroshiro);

const kuroshiro = new Kuroshiro();
await kuroshiro.init(new KuromojiAnalyzer());

// async function furigana_one(sentence, mode_str, to_str) {
//     return await kuroshiro.convert(sentence, {mode: mode_str, to: to_str});
//     // console.log(kuroshiro.convert(sentence, {mode:"furigana", to: "hiragana"}));
// }
// const result = await kuroshiro.convert("感じ取れたら手を繋ごう、重なるのは人生のライン and レミリア最高！", {mode:"furigana", to:"hiragana"});
// const result = await furigana_one(process.argv[2], process.argv[3], process.argv[4])
// console.log(result);
app.use(Express.json());
app.use(Express.urlencoded({ extended: true }));

app.post("/furigana", async (req, res) => {
    if (!('sentence' in req.body && 'mode_str' in req.body && 'to_str' in req.body)) {
        res.send('Invalid request')
    } else {
        const result = await kuroshiro.convert(req.body.sentence, {mode: req.body.mode_str, to: req.body.to_str});
        res.send(result);
    }
});

app.get("/furigana/exit", (req, res) => {
    console.log('Furigana server exit')
    res.send('bye')
    server.close()
});

const server = app.listen(process.argv[2], () => {
    console.log('Furigana server starts on ' + process.argv[2])
});
