"""Inference View."""

from django.shortcuts import JsonResponse

import numpy as np
from sklearn.decomposition import PCA
from sklearn.decomposition import StandardScaler
import bmcc

from UserProfile.models import UserProfile, DataCapture


def _hybrid(*args, **kwargs):
    """Hybrid sampler."""
    for _ in range(5):
        bmcc.gibbs(*args, **kwargs)
    bmcc.split_merge(*args, **kwargs)


def _model(x, asn, sampler=hybrid, alpha=0.1, annealing=None):
    """Create clustering model."""
    return bmcc.BayesianMixture(
        data=x,
        sampler=sampler,
        component_model=bmcc.NormalWishart(
            df=ds.dim, scale=np.identity(ds.dim) * np.sqrt(ds.dim)),
        mixture_model=bmcc.DPM(alpha=alpha, use_eb=False),
        annealing=annealing,
        assignments=asn,
        thinning=10)


def _majority_filter(y, ksize=60):
    """Sliding window majority filter."""
    y_new = np.zeros_like(y)
    for i, _ in enumerate(y):
        neighborhood = y[max(0, i - ksize): min(i + ksize, y.shape[0] - 1)]
        y_new[i] = mode(neighborhood)[0][0]
    return y_new


def _list_segments(z):
    """Extract segments from clusters."""
    changes = np.where(z[:-1] != z[1:])[0]

    segments = []
    start = 0
    for end in changes:
        if end - start > 60:
            segments.append({
                "start": start,
                "end": end,
                "id": z[end - 1]
            })
            start = end + 1

    segments.append({"start": start, "end": len(z), "id": z[-1]})
    return segments


def do_inference(request):
    """Main inference view."""
    if request.method != 'POST':
        return JsonResponse{"error": "Request is not POST."}

    # Fetch data
    session = request.POST.get("session")
    user = UserProfile.objects.get(pk=user)

    data = DataCapture.objects.filter(user=user, sessionid=session)
    image_stack = np.stack([
        np.frombuffer(obj.img, dtype=np.float32) for obj in data])

    # Prepare features
    x = StandardScaler().fit_transform(
        PCA(n_components=3).fit_transform(
            StandardScaler().fit_transform(image_stack))).astype(np.float64)
    n = x.shape[0]

    # Cluster
    model = _model(
        x, np.zeros(ds.n, dtype=np.uint16),
        alpha=0.1, sampler=hybrid)
    model.iter(10)

    model = _model(
        x, np.copy(model.hist[-1]), alpha=1,
        sampler=bmcc.temporal_gibbs, annealing=lambda n: 0.05 * n)
    model.iter(200)

    # Filter
    _, residuals = bmcc.pairwise_probability(model.hist, 10)
    best = model.hist[np.argmin(residuals) + 10]

    filtered = _majority_filter(best)
    segments = _list_segments(filtered)

    return JsonResponse({
        "activities": segments
    })
