/* 着陆页交互。只做两件事：提交订阅、把结果告诉用户。
   变体分流完全在服务端完成，此处不参与实验逻辑。 */
(function () {
  "use strict";

  var form = document.getElementById("signup");
  var msg = document.getElementById("form-msg");
  var email = document.getElementById("email");
  var channel = document.getElementById("source_channel");
  var submit = form.querySelector("button[type=submit]");

  function say(text, kind) {
    msg.textContent = text;
    msg.className = "form-msg " + (kind || "");
  }

  form.addEventListener("submit", function (ev) {
    ev.preventDefault();

    if (!email.value.trim()) {
      say("请填写邮箱地址。", "err");
      email.focus();
      return;
    }
    if (!channel.value) {
      say("请选择你从哪里了解到我们——这会帮助我们判断渠道效果。", "err");
      channel.focus();
      return;
    }

    submit.disabled = true;
    say("提交中…", "");

    fetch("/api/subscribers", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: email.value.trim(),
        source_channel: channel.value,
        ab_variant: window.AJ_VARIANT || "",
        company: document.getElementById("company").value
      })
    })
      .then(function (r) {
        return r.json().then(function (d) { return { status: r.status, data: d }; });
      })
      .then(function (res) {
        if (res.data && res.data.ok) {
          say(res.data.created
            ? "已加入。上线时我们会第一时间通知你。"
            : "你已经在名单里了，无需重复订阅。", "ok");
          form.reset();
        } else {
          say((res.data && res.data.error) || "提交失败，请稍后再试。", "err");
          submit.disabled = false;
        }
      })
      .catch(function () {
        say("网络错误，请稍后再试。", "err");
        submit.disabled = false;
      });
  });
})();