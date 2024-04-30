# `Cloudflare Worker`

***Use with discretion!***

>Having issues with unreachable hosts that should be reachable?

## 📝 Table of Contents

- [Prerequisites](#prerequisites)
- [Running](#running)

## 1️⃣ Prerequisites <a name = "prerequisites"></a>

Need to have [Cloudflare Workers](https://workers.cloudflare.com/), and coded like below:

```
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  // Extract the value of the 'url' query parameter
  const urlParam = new URL(request.url).searchParams.get('url')
  
  // console.log(urlParam.toString())
  if (!urlParam) {
    return new Response('URL parameter is missing', { status: 400 })
  }

  try {
    return await fetch(urlParam.toString(), {
      headers: {
        "X-Source": "Cloudflare-Workers",
      },
    });
  } catch (error) {
    // If an error occurs during fetching, return an error response
    return new Response('Error fetching URL', { status: 500 })
  }
}

```

Test your `worker` by sending a request like `https://xxxworker.xxxname.workers.dev/?url=some-url` or just open it in a
browser or use the online editor

## 🎈 Running <a name = "running"></a>

Set your worker url either in the `.env` where it is named `CF=xxx` or pass it through arguments `-cf xxx`

(Optional) You could also configure the priority, which does not support *arguments*, only environment variables which
is in the config file named `cf_priority`, defaults to `False`, but you could set to `True` which would use Cloudflare
first.
