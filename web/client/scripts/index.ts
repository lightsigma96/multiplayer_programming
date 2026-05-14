addEventListener("DOMContentLoaded", async () => {

	const form = document.getElementById("login_form") as HTMLFormElement
	const username_box = document.getElementById("username") as HTMLInputElement
	const password_box = document.getElementById("password") as HTMLInputElement

	const response: Response = await fetch("http://localhost:8000/", {
		method: "POST",
		credentials: "include"
	})
	const response_json = await response.json()

	console.log(response_json)

	form.addEventListener("submit", () => {
		const username: string = username_box.value
		const password: string = password_box.value

		fetch("http://localhost:8000/login", {
			"method": "POST",
			"credentials": "include",
			"body": JSON.stringify({
				"username": username,
				"password": password
			}
			)
		})
	})
})

