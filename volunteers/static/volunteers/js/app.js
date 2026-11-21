const tg = window.Telegram.WebApp;


/*
 * Сообщаем Telegram,
 * что приложение готово.
 */
tg.ready();


/*
 * Растягиваем Mini App
 * на доступную высоту.
 */
tg.expand();


/*
 * Используем цвета Telegram,
 * если они доступны.
 */
if (tg.themeParams) {
    document.documentElement.style.setProperty(
        "--tg-bg",
        tg.themeParams.bg_color || "#f5f7fb"
    );

    document.documentElement.style.setProperty(
        "--tg-text",
        tg.themeParams.text_color || "#172033"
    );
}


/*
 * Получаем информацию
 * о пользователе Telegram.
 */
const user = tg.initDataUnsafe?.user;


if (user) {

    const name = user.first_name || "Пользователь";

    const title = document.querySelector(".header h1");

    if (title) {
        title.textContent = `Добро пожаловать, ${name} 👋`;
    }
}
function openPage(url) {
    window.location.href = url;
}