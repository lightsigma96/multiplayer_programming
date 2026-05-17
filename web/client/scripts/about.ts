async function about_request_token() {
	try {
		const response: Response = await fetch("http://localhost:8000/about", {
			method: "GET",
			credentials: "include"
		})
		const response_json = await response.json()
		console.log(response_json)

	} catch (e) { console.error(e) }
}
about_request_token()
