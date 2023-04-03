from django.urls import reverse


def admin_hook(context):
    return """
    <li>
        <a href="{url}">
            <i class="fa fa-arrow-circle-right"></i> Commission Articles
        </a>
    </li>
    """.format(url=reverse('commission_index'))
