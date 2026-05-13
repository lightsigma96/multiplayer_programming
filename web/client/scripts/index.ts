addEventListener("DOMContentLoaded", () => {

	const cookie_btn = document.getElementById("set-cookies") as HTMLButtonElement

	cookie_btn.addEventListener("click", async () => {
		const response: Response = await fetch("http://localhost:8000/", {
			method: "POST",
			credentials: "include"
		})
		const response_json = await response.json()

		console.log(response_json)
	})

})

