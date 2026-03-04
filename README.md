# Alliance Auth Ballot Box

A secure, feature-rich polling and voting application for Alliance Auth. Empower your alliance leadership to create targeted, verifiable measures and gather community feedback effortlessly.

## ✨ Key Features

* **Targeted Voting:** Restrict access to specific polls based on Alliance Auth **Groups** and/or **States** (e.g., restrict a vote to only full members or specific sigs).
* **Smart Notifications:** A native sidebar bubble instantly alerts users when an active measure requires their vote.
* **Flexible Visibility:** Choose exactly who sees the results. Make them public to eligible voters, restrict them to leadership only, or automatically hide them until the poll officially closes.
* **Rich Text Descriptions:** Fully supports Markdown for detailed, beautifully formatted ballot measures. Includes a live preview editor right in the admin panel.
* **Dynamic Analytics:** Visualizes final vote tallies using clean, interactive pie charts (powered by Chart.js).
* **Secure Voting:** Users can cast and update their votes securely at any time before the deadline.

---

## 🛠️ Installation

**1. Install the App**
Steps depend on your environment (docker vs baremetal)

**2. Configure Alliance Auth**
Open your `local.py` settings file and add `'ballotbox'` to your `INSTALLED_APPS` list:
```python
INSTALLED_APPS += [
    'ballotbox',
]
```

**3. Apply initial Migrations**

**4. Collect Static Files**

**5. Restart Supervisor/Alliance Auth**

---

## 🔐 Permissions

To access the app, users will need the appropriate permissions assigned to their State or Group in the Alliance Auth admin panel.

| Permission | Description |
| :--- | :--- |
| `ballotbox.basic_access` | **Voter:** Grants access to the Ballot Box dashboard. Users can only see and vote on measures they are eligible for. |
| `ballotbox.manage_ballots` | **Leadership:** Can view the results of *all* measures regardless of visibility settings, and access the Django Admin panel to create new polls. |

---

## 📝 Creating a Ballot

1. Navigate to your Django Admin panel (`/admin`).
2. Scroll down to **Ballotbox** and click **Ballots** -> **Add**.
3. Fill out the Title, Description (Markdown/html supported), and set your Closing Date.
4. **Visibility:** * Check `Public Results` if you want voters to see the outcome.
    * Check `Hide Results Until Closed` to keep the tallies secret while the poll is active.
5. **Restrictions:** Select specific Allowed Groups or States. *(Leave these completely blank to make it an alliance-wide vote).*
6. Add your voting options at the bottom of the page and click **Save**.
