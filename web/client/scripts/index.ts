const form = document.getElementById("login_form") as HTMLFormElement
const username_box = document.getElementById("username") as HTMLInputElement
const password_box = document.getElementById("password") as HTMLInputElement

async function index_request_token() {
	try {
		const response: Response = await fetch("http://localhost:8000/home", {
			method: "GET",
			credentials: "include"
		})
		const response_json = await response.json()
		console.log(response_json)

	} catch (e) { console.error(e) }
}
index_request_token()

/* async function init() {
	try {
		const response: Response = await fetch("http://localhost:8000/", {
			method: "POST",
			credentials: "include"
		})
		const response_json = await response.json()
		console.log(response_json)

	} catch (e) { console.error(e) }
}
init() */

form.addEventListener("submit", async (e) => {
	e.preventDefault()
	const username: string = username_box.value
	const password: string = password_box.value

	const res = await fetch("http://localhost:8000/sign_up", {
		"method": "POST",
		"credentials": "include",
		"headers": {
			"Content-Type": "application/json"
		},
		"body": JSON.stringify({
			"username": username,
			"password": password
		}
		)
	})

	const res_json = await res.json()
	console.log(res_json)
})


