{% for item in items %}
* :obj:`{{ item.name }} <{{ item.full_name }}>`
{% endfor %}
