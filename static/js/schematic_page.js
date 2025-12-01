// static/script.js
const $ = (sel) => document.querySelector(sel);

function notify(msg) {
  // Vervang dit met fetch() naar je backend routes (link/commit/next/prev)
  console.log(msg);
  alert(msg);
}

$("#btn-link")?.addEventListener("click", () => notify("Link action triggered"));
$("#btn-commit")?.addEventListener("click", () => notify("Commit action triggered"));
$("#btn-prev")?.addEventListener("click", () => notify("Previous page"));
$("#btn-next")?.addEventListener("click", () => notify("Next page"));

$("#kast-type")?.addEventListener("change", (e) => {
  notify(`Kast type: ${e.target.value}`);
});

$("#pagina-nr")?.addEventListener("change", (e) => {
  notify(`Pagina nr: ${e.target.value}`);
});
